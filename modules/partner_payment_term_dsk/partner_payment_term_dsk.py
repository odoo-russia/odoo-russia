#coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv

class res_partner(osv.osv):
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        for partner in self.browse(cr, uid, ids, context=context):
            #TODO: create or update payment terms

    _name = 'res.partner'
    _inherit = 'res.partner'
    _columns = {
        'contract_expiration_date': fields.date('Contract expiration date'),
        'payment_deferment': fields.integer('Deferment of payment'),
    }
res_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: