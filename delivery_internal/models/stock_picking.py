# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.depends('carrier_id')
    def depends_carrier_id(self):
        print 'Called!'
        carrier = self.carrier_id
        if carrier.delivery_type == 'internal':
            self.env['stock.pickup.request'].create({
                'picking_id': self.id,
                'company_id': carrier.internal_delivery_company.id,
            })
