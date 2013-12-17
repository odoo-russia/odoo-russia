# -*- coding: utf-8 -*-
from openerp.osv import osv, fields


class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'factoring': fields.boolean('Factoring'),
        'factoring_conditions': fields.text('Factoring conditions'),
    }