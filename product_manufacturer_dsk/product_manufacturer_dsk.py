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

class product_manufacturer(osv.osv):
    _name = 'product.manufacturer'
    _columns = {
        'name': fields.many2one('res.partner', 'Manufacturer', required=True),
        'product_name': fields.char('Manufacturer Product Name', size=64),
        'product_code': fields.char('Manufacturer Product Code', size=64),
        'product_id': fields.many2one('product.product', 'Product', required=True, ondelete='cascade'),
    }
    _sql_constraints = [('manufacturer_product_id_unique','unique(product_id, name)', 'Each manufacturer can be selected only one time!')]
product_manufacturer()

class product_product(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'
    _columns = {
        'manufacturer_ids' : fields.one2many('product.manufacturer','product_id','Manufacturers'),
    }
product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: