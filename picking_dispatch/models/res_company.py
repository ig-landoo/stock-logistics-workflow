# -*- coding: utf-8 -*-
# Copyright 2012-2014 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ResCompany(models.Model):
    _name = 'res.company'
    _inherit = 'res.company'

    default_picker_id = fields.Many2one(
        'res.users',
        'Default Picker',
        help='The user to which the pickings are assigned by default',
        select=True,
    )
