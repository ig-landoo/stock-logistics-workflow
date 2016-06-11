# -*- coding: utf-8 -*-
# Copyright 2012-2014 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    dispatch_id = fields.Many2one(
        string='Dispatch',
        comodel_name='picking.dispatch',
        select=True,
        help='who this move is dispatched to',
    )

    @api.multi
    def copy_data(self, default=None):
        if default is None:
            default = {}
        default = default.copy()
        default['dispatch_id'] = False
        return super(StockMove, self).copy_data(default=default)

    @api.multi
    def do_partial(self, partial_datas):
        """
        in addition to what the original method does, create backorder
        picking.dispatches and set the state of picing.dispatch
        according to the state of moves state
        """
        dispatch_obj = self.env['picking.dispatch']
        _logger.debug('partial stock.moves %s %s', self, partial_datas)
        complete_move_ids = super(StockMove, self).do_partial(partial_datas)
        # in complete_move_ids, we have:
        # * moves that were fully processed
        # * newly created moves (the processed part of partially processed
        #   moves) belonging to the same dispatch as the original move
        # so the difference between the original set of moves and the
        # complete_moves is the set of unprocessed moves
        unprocessed_move_ids = self - set(complete_move_ids)
        _logger.debug(
            'partial stock.moves: complete_move_ids %s, '
            'unprocessed_move_ids %s',
            complete_move_ids, unprocessed_move_ids)
        # unprocessed moves are still linked to the dispatch : this dispatch
        # must not be marked as Done
        unfinished_dispatch_ids = {}
        for move in unprocessed_move_ids:
            if not move.dispatch_id:
                continue
            # value will be set later to a new dispatch
            unfinished_dispatch_ids[move.dispatch_id.id] = None
        maybe_finished_dispatches = {}
        for move in complete_move_ids:
            if not move.dispatch_id:
                continue
            dispatch_id = move.dispatch_id.id
            if dispatch_id in unfinished_dispatch_ids:
                # the dispatch was partially processed: we need to link the
                # move to a new dispatch containing only fully processed moves
                if unfinished_dispatch_ids[dispatch_id] is None:
                    # create a new dispatch, and record its id
                    _logger.debug(
                        'create backorder picking.dispatch of %s', dispatch_id)
                    new_dispatch_id = dispatch_obj.copy({
                        'backorder_id': dispatch_id,
                    })
                    unfinished_dispatch_ids[dispatch_id] = new_dispatch_id
                dispatch_id = unfinished_dispatch_ids[dispatch_id]
            maybe_finished_dispatches.setdefault(
                dispatch_id, []).append(move.id)
        for dispatch_id, move_ids in maybe_finished_dispatches.iteritems():
            move_ids.write({'dispatch_id': dispatch_id})
        dispatch_obj.check_finished(list(maybe_finished_dispatches))
        dispatch_obj.write(list(unfinished_dispatch_ids),
                           {'state': 'assigned'})
        return complete_move_ids

    @api.multi
    def action_cancel(self):
        """
        in addition to what the method in the parent class does,
        cancel the dispatches for which all moves where cancelled
        """
        _logger.debug('cancel stock.moves %s', self)
        status = super(StockMove, self).action_cancel()
        if not len(self):
            return True
        dispatch_obj = self.env['picking.dispatch']
        dispatch_ids = dispatch_obj.browse()
        for move in self:
            if move.dispatch_id:
                dispatch_ids += move.dispatch_id
        for dispatch in dispatch_ids:
            if any(move.state != 'cancel' for move in dispatch.move_ids):
                dispatch_ids -= dispatch
        if len(dispatch_ids):
            _logger.debug(
                'set state to cancel for picking.dispatch %s',
                list(dispatch_ids))
            dispatch_ids.write({'state': 'cancel'})
        return status

    @api.multi
    def action_done(self):
        """
        in addition to the parent method does, set the dispatch done if all
        moves are done or canceled
        """
        _logger.debug('done stock.moves %s', self)
        status = super(StockMove, self).action_done()
        if not len(self):
            return True
        dispatch_obj = self.env['picking.dispatch']
        dispatch_ids = dispatch_obj.browse()
        for move in self:
            if move.dispatch_id:
                dispatch_ids += move.dispatch_id
        dispatch_ids.check_finished()
        return status
