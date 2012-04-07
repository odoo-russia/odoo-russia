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
    _name = 'product.product'
    _inherit = 'product.product'
    _columns = {
        'name_eshop': fields.char('Name for E-shop', size=200),
    }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        name = vals.get('name')
        name_eshop = vals.get('name_eshop')

        if name_eshop and not name:
            vals['name'] = name_eshop
        elif name and not name_eshop:
           vals['name_eshop'] = name

        return super(product_product, self).create(cr, uid, vals, context)
product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: