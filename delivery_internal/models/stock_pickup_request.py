# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockPickupRequest(models.Model):
    _name = 'stock.pickup.request'
    _description = 'Stock Pickup Request'

    name = fields.Char(
        string='Pickup Name',
        default=lambda x: x._default_name(),
    )
    company_id = fields.Many2one(
        string='Responsible Company',
        comodel_name='res.company',
        required=True,
    )
    cash_on_delivery = fields.Boolean(
        string='Cash On Delivery',
        default=0,
    )
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('confirmed', 'Confirmed'),
            ('complete', 'Completed')
        ],
        compute='_compute_state',
        store=True,
    )
    picking_id = fields.Many2one(
        string='Source Picking',
        comodel_name='stock.picking',
        required=True,
    )
    in_picking = fields.Many2one(
        string='Inbound Buyer Picking',
        comodel_name='stock.picking',
    )
    out_picking = fields.Many2one(
        string='Carrier Pickup Picking',
        comodel_name='stock.picking',
    )
    cash_in_picking = fields.Many2one(
        string='Cash Picking From Buyer Picking',
        comodel_name='stock.picking',
    )
    cash_out_picking = fields.Many2one(
        string='Cash Delivery From Carrier Picking',
        comodel_name='stock.picking',
    )

    @api.depends('in_picking.state', 'out_picking.state')
    def _compute_state(self):
        """ It will compute the status of the pickup based on the delivery
         pickings """
        state = 'new'
        if self.in_picking.state == 'confirmed' and self.out_picking.state == \
                'confirmed':
            state = 'confirmed'
        elif self.in_picking.state == 'done' and self.out_picking.state == \
                'done':
            state = 'complete'
        self.state = state

    def _default_name(self):
        """ It should return the next sequence for the model to use as a
        name
        Returns:
            (str): Sequence code to use as a name
        """
        return self.env['ir.sequence'].next_by_code('stock.picking.request')

    @api.depends('cash_on_delivery')
    def _cod_create_pickings(self):
        """ It will create CoD pickings when CoD is selected in the RFP """
        if not self.cash_on_delivery:
            return
        carrier = self.picking_id.carrier_id
        pick_type = carrier.internal_delivery_money_picking_type
        self.cash_in_picking = self.env['stock.picking'].create({
            'location_id': pick_type.default_location_src_id.id,
            'location_dest_id': self.picking_id.location_dest_id.id,
            'picking_type_id': pick_type.id,
            'partner_id': self.picking_id.partner_id.id,
            'move_type': 'one',
        })
        self.cash_out_picking = self.env['stock.picking'].create({
            'location_id': self.picking_id.location_id.id,
            'location_dest_id': pick_type.default_location_src_id.id,
            'picking_type_id': pick_type.id,
            'partner_id': self.company_id.partner_id.id,
            'move_type': 'one',
        })


    def create(self, vals):
        """ It should create the pickings for the delivery on create """
        create = super(StockPickupRequest, self).create(vals)
        picking = self.env['stock.picking'].browse(vals.get('picking_id'))
        carrier = picking.carrier_id
        print carrier
        pick_type = carrier.internal_delivery_stock_picking_type
        self.in_picking = self.env['stock.picking'].create({
            'location_id': pick_type.default_location_src_id.id,
            'location_dest_id': self.picking_id.location_dest_id.id,
            'picking_type_id': pick_type.id,
            'partner_id': self.picking_id.partner_id.id,
            'move_type': 'one',
        })
        self.out_picking = self.env['stock.picking'].create({
            'location_id': self.picking_id.location_id.id,
            'location_dest_id': pick_type.default_location_src_id.id,
            'picking_type_id': pick_type.id,
            'partner_id': self.company_id.partner_id.id,
            'move_type': 'one',
        })
        return create
