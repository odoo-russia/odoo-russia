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

class product_product(osv.osv):
    def is_description(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        res = {}
        for product in self.browse(cr, uid, ids, context=context):
            if product.description:
                res[product.id] = True
            else:
                res[product.id] = False
        return res

    _name = 'product.product'
    _inherit = 'product.product'
    _columns = {
        'description_short': fields.char('Short description', size=200),
        'is_description': fields.function(is_description, type='boolean', store=False, string='Description'),
    }
product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: