# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestCommon(TransactionCase):

    def setUp(self):
        super(TestCommon, self).setUp()
        location = self.env['stock.location'].search([])[0]
        self.partner_id = self.env['res.partner'].create({'name': 'Carrier'})
        self.picking_type = self.env['stock.picking.type'].search([])[0]
        self.picking_type.write({'default_location_src_id': location.id})
        self.picking_id = self.env['stock.picking'].create({
            'partner_id': self.partner_id.id,
            'location_dest_id': location.id,
            'location_id': location.id,
            'picking_type_id': self.picking_type.id,
        })

        self.service_id = self.env['delivery.carrier'].create({
            'name': 'Test Method',
            'delivery_type': 'internal',
            'internal_delivery_company':
                self.env['res.company'].search([])[0].id,
            'internal_delivery_stock_picking_type': self.picking_type.id,
            'internal_delivery_money_picking_type': self.picking_type.id
        })
        self.picking_id.carrier_id = self.service_id#({'carrier_id': })
