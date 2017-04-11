# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from .common import TestCommon


class TestStockPickupRequest(TestCommon):

    def test_creates_pickings_on_create(self):
        """ It should create two pickings on create """
        obj = self.env['stock.pickup.request'].create({
            'company_id': self.service_id.internal_delivery_company.id,
            'picking_id': self.picking_id.id,
        })
        pickings = [obj.in_picking.id, obj.out_picking.id]
        self.assertTrue(None not in pickings)

    def test_creates_cod_pickings(self):
        """ It should create pickings on CoD True"""
        obj = self.env['stock.pickup.request'].create({
            'company_id': self.service_id.internal_delivery_company.id,
            'picking_id': self.picking_id.id,
        })
        obj.cash_on_delivery = True
        pickings = [obj.cash_in_picking.id, obj.cash_in_picking.id]
        self.assertTrue(None not in pickings)
        self.assertEquals(
            self.cash_out_picking.location_id.id ==
            self.picking_id.location_id.id
        )

    def test_compute_state_new(self):
        """ It should default to new """
        obj = self.env['stock.pickup.request'].create({
            'company_id': self.service_id.internal_delivery_company.id,
            'picking_id': self.picking_id.id,
        })
        self.assertEquals(obj.state == 'new')

