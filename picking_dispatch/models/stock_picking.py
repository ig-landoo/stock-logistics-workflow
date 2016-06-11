# -*- coding: utf-8 -*-
# Copyright 2012-2014 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    related_dispatch_ids = fields.One2many(
        string='Related Dispatch Picking',
        comodel_name='picking.dispatch',
        compute='_get_related_dispatch',
        search='_search_dispatch_pickings',
    )

    @api.multi
    def _get_related_dispatch(self, field_names, arg=None):
        result = {}
        if not len(self):
            return result
        for pick_id in self:
            result[pick_id.id] = []
        sql = ("SELECT DISTINCT sm.picking_id, sm.dispatch_id "
               "FROM stock_move sm "
               "WHERE sm.picking_id in %s AND sm.dispatch_id is NOT NULL")
        self.env.cr.execute(sql, (result.keys()))
        res = self.env.cr.fetchall()
        for picking_id, dispatch_id in res:
            result[picking_id].append(dispatch_id)
        return result

    @api.multi
    def _search_dispatch_pickings(self, name, args):
        if not len(args):
            return []
        picking_ids = set()
        for field, symbol, value in args:
            move_ids = self.env['stock.move'].search(
                [('dispatch_id', symbol, value)]
            )
            picking_ids.add(m.picking_id.id for m in move_ids)
        return [('id', 'in', list(picking_ids))]
