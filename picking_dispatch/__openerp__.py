# -*- coding: utf-8 -*-
# Copyright 2012 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{'name': 'Picking dispatch',
 'version': '9.0.1.0.0',
 'author': "Camptocamp, LasLabs, Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp, LasLabs',
 'category': 'Products',
 'complexity': "normal",  # easy, normal, expert
 'depends': ['stock',
             'delivery',
             ],
 'website': 'http://www.camptocamp.com/',
 'data': ['views/picking_dispatch_view.xml',
          'data/picking_dispatch_sequence_data.xml',
          'wizards/create_dispatch_view.xml',
          'wizards/dispatch_assign_picker_view.xml',
          'wizards/dispatch_start_view.xml',
          'wizards/check_assign_all_view.xml',
          'report/report_picking_dispatch.xml',
          'views/picking_dispatch_report.xml',
          'data/ir_cron_data.xml',
          'security/ir.model.access.csv',
          'security/security.xml',
          # 'picking_dispatch_workflow.xml',
          ],
 'installable': True,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': False
 }
