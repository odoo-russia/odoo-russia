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
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        mrp_width = vals.get('mrp_width', 0)
        mrp_height = vals.get('mrp_height', 0)
        if mrp_height > mrp_width:
            mrp_width, mrp_height = mrp_height, mrp_width
            vals['mrp_width'] = mrp_width
            vals['mrp_height'] = mrp_height
        return super(product_product, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (list)):
            if len(ids) > 1:
                raise osv.except_osv(_('Error'), _('There is more than one product to update MRP sizes.\
                                                    Please ask your programmer to fix the error!'))
            else:
                ids = ids[0]
        mrp_width = vals.get('mrp_width', self.browse(cr, uid, ids, context).mrp_width)
        mrp_height = vals.get('mrp_height', self.browse(cr, uid, ids, context).mrp_height)
        if mrp_height > mrp_width:
            mrp_width, mrp_height = mrp_height, mrp_width
            vals['mrp_width'] = mrp_width
            vals['mrp_height'] = mrp_height
        return super(product_product, self).write(cr, uid, ids, vals, context=context)


    _name = 'product.product'
    _inherit = 'product.product'
    _columns = {
        'mrp_width': fields.integer('Width, mm', size=5, help="Width in mm"),
        'mrp_height': fields.integer('Height, mm', size=5, help="Height in mm"),
        'mrp_has_pattern': fields.boolean('Has a pattern (only for materials)'),
        'mrp_across_pattern': fields.boolean('Across the pattern (only for details)'),
        'mrp_category_id': fields.many2one(),
    }
product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: