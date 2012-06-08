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

class product_brand(osv.osv):
    def _get_filename(self, full_path):
        return full_path.replace('\\', '/').split('/')[-1]

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        image_path = vals.get('logo_filename')
        if image_path:
            vals['logo_filename'] =  self._get_filename(image_path)
        return super(product_brand, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        image_path = vals.get('logo_filename')
        if image_path:
            vals['logo_filename'] =  self._get_filename(image_path)
        return super(product_brand, self).write(cr, uid, ids, vals, context)

    _name = 'product.brand'
    _columns = {
        'name': fields.char('Brand', size=64, required=True),
        'description': fields.text('Description'),
        'logo': fields.binary('Logo', required=True),
        'logo_filename': fields.char('Logo filename', size=500),
        'partner_id': fields.many2one('res.partner', 'Partner', help='Select partner for this Brand', required=True,
                                      ondelete='restrict'),
    }
product_brand()

class product_manufacturer(osv.osv):
    def _check_references(self, cr, uid, ids):
        for manufacturer in self.browse(cr, uid, ids):
            if manufacturer.product_brand_id and manufacturer.product_brand_id.partner_id != manufacturer.name:
                return False
        return True

    def onchange_manufacturer(self, cr, uid, ids, name):
        return {'value': {'product_brand_id': False}}

    _name = 'product.manufacturer'
    _columns = {
        'name': fields.many2one('res.partner', 'Manufacturer', required=True, ondelete='restrict',
                                context='{"form_view_ref": "eshop_base_dsk.res_partner_form_view_eshop_dsk"}'),
        'product_name': fields.char('Manufacturer Product Name', size=64),
        'product_code': fields.char('Manufacturer Product Code', size=64),
        'product_country_id': fields.many2one('res.country', 'Country', ondelete='restrict'),
        'product_brand_id': fields.many2one('product.brand', 'Brand', ondelete='restrict'),
        'product_id': fields.many2one('product.product', 'Product', required=True, ondelete='cascade'),
    }
    _sql_constraints = [('manufacturer_product_id_unique','unique(product_id, name)', 'Each manufacturer can be \
                        selected only one time!')]
    _constraints = [
        (_check_references, 'Manufacturer isn\'t owner of this brand! Select another.', ['product_brand_id'])
    ]
product_manufacturer()

class product_product(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'
    _columns = {
        'manufacturer_ids' : fields.one2many('product.manufacturer','product_id','Manufacturers'),
    }
product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: