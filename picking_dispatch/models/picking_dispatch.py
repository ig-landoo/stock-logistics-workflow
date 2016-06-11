# -*- coding: utf-8 -*-
# Copyright 2012-2014 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from datetime import datetime
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PickingDispatch(models.Model):

    """New object that contain stock moves selected from stock.picking by the
    warehouse manager so that the warehouseman can go and bring the product
    where they're asked for.  The purpose is to know who will look for what in
    the warehouse. We don't use the stock.picking object cause we don't want to
    break the relation with the SO and all related workflow.

    This object is designed for the warehouse problematics and must help the
    people there to organize their work."""

    _name = 'picking.dispatch'
    _description = "Dispatch Picking Order"

    name = fields.Char(
        'Name',
        required=True, select=True,
        copy=False, unique=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env['ir.sequence'].get('picking.dispatch'),
        help='Name of the picking dispatch')
    date = fields.Date(
        'Date',
        required=True, readonly=True, select=True,
        states={'draft': [('readonly', False)],
                'assigned': [('readonly', False)]},
        default=fields.Date.context_today,
        help='Date on which the picking dispatched is to be processed')
    picker_id = fields.Many2one(
        'res.users', 'Picker',
        readonly=True, select=True,
        states={'draft': [('readonly', False)],
                'assigned': [('readonly', False),
                             ('required', True)]},
        help='The user to which the pickings are assigned')
    move_ids = fields.One2many(
        'stock.move', 'dispatch_id', 'Moves',
        readonly=True, copy=False,
        states={'draft': [('readonly', False)]},
        help='The list of moves to be processed')
    notes = fields.Text('Notes', help='free form remarks')
    backorder_id = fields.Many2one(
        'picking.dispatch', 'Back Order of',
        help='If this dispatch was split, this links to the dispatch '
        'order containing the other part which was processed',
        select=True)
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('assigned', 'Assigned'),
            ('progress', 'In Progress'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
        ], 'Dispatch State',
        readonly=True, select=True, copy=False,
        default='draft',
        help='The state of the picking. '
        'Workflow is draft -> assigned -> progress -> done or cancel')
    related_picking_ids = fields.One2many(
        'stock.picking',
        readonly=True,
        string='Related Dispatch Picking',
        compute='_compute_related_picking')
    company_id = fields.Many2one(
        'res.company', 'Company',
        required=True,
        default=lambda s: s._default_company(),
    )

    @api.multi
    def _compute_related_picking(self):
        if not self.ids:
            return

        cr = self.env.cr
        picking_ids = {}
        for dispatch in self:
            picking_ids[dispatch.id] = []
        sql = ("SELECT DISTINCT sm.dispatch_id, sm.picking_id "
               "FROM stock_move sm "
               "WHERE sm.dispatch_id in %s AND sm.picking_id is NOT NULL")
        cr.execute(sql, (tuple(self.ids),))
        res = cr.fetchall()
        for line in res:
            picking_ids[line[0]].append(line[1])
        for dispatch in self:
            # Must set None or will try to access it before being computed
            dispatch.related_picking_ids = None
            dispatch.related_picking_ids = [(6, 0, picking_ids[dispatch.id])]

    @api.model
    def _default_company(self):
        company_obj = self.env['res.company']
        return company_obj._company_default_get('picking.dispatch')

    @api.multi
    @api.constrains('picker_id')
    def _check_picker_assigned(self):
        for dispatch in self:
            if (dispatch.state in ('assigned', 'progress', 'done') and
                    not dispatch.picker_id):
                raise ValidationError(_('Please select a picker.'))
        return True

    @api.multi
    def action_assign(self):
        _logger.debug('set state to assigned for picking.dispatch %s', self)
        self.write({'state': 'assigned'})
        return True

    @api.multi
    def action_progress(self):
        self.assert_start_ok()
        _logger.debug('set state to progress for picking.dispatch %s', self)
        self.write({'state': 'progress'})
        return True

    @api.multi
    def action_done(self):
        domain = [('dispatch_id', 'in', self.ids)]
        moves = self.env['stock.move'].search(domain)
        return moves.action_done()

    @api.multi
    def check_finished(self):
        """set the dispatch to finished if all the moves are finished"""
        finished = self.browse()
        for dispatch in self:
            if all(move.state in ('cancel', 'done')
                   for move in dispatch.move_ids):
                finished |= dispatch
        _logger.debug('set state to done for picking.dispatch %s', finished)
        finished.write({'state': 'done'})
        return finished

    @api.multi
    def action_cancel(self):
        domain = [('dispatch_id', 'in', self.ids)]
        moves = self.env['stock.move'].search(domain)
        res = moves.action_cancel()
        # If dispatch is empty, we still need to cancel it !
        if not moves:
            _logger.debug('set state to cancel for picking.dispatch %s', self)
            self.write({'state': 'cancel'})
        return res

    @api.multi
    def assert_start_ok(self):
        now = datetime.now().date()
        for obj in self:
            date = datetime.strptime(obj.date, '%Y-%m-%d').date()
            if now < date:
                raise ValidationError(
                    _('This dispatch cannot be processed until %s') % obj.date
                )

    @api.multi
    def action_assign_moves(self, context=None):
        move_ids = self.env['stock.move'].search([
            ('dispatch_id', 'in', [r.id for r in self])
        ])
        move_ids.action_assign()
        return True

    @api.multi
    def check_assign_all(self, domain=None):
        """ Try to assign moves of a selection of dispatches

        Called from a cron
        """
        pickings = self
        if not pickings:
            if domain is None:
                domain = [('state', 'in', ('draft', 'assigned'))]
            pickings = self.search(domain)
        pickings.action_assign_moves()
        return True
