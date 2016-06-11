# -*- coding: utf-8 -*-
# Copyright 2012-2014 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ProductProduct(models.Model):
    _inherit = "product.product"

    description_warehouse = fields.Text(
        'Warehouse Description',
        translate=True,
    )
