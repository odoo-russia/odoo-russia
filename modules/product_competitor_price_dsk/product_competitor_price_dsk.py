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

class product_competitor(osv.osv):
    _name = 'product.competitor'
    _columns = {
        'name': fields.many2one('res.partner', 'Competitor', required=True, ondelete='restrict',
            context='{"form_view_ref": "eshop_base_dsk.res_partner_form_view_eshop_dsk"}'),
        'product_id': fields.many2one('product.product', 'Product Id', required=True, ondelete='cascade'),
        'similar_product_name': fields.char('Similar product name', size=128),
        'similar_product_url': fields.char('Similar product URL', size=128),
        'similar_product_price': fields.float('Price for similar product', digits=(10,2), required=True),
    }
product_competitor()

class product_product(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'
    _columns = {
        'competitor_ids': fields.one2many('product.competitor', 'product_id', 'Competitors'),
    }
product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: