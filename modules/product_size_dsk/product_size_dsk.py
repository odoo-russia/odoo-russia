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
        'width': fields.integer('Width', size=5, help="Width in mm"),
        'height': fields.integer('Height', size=5, help="Height in mm"),
        'depth': fields.integer('Depth', size=5, help="Depth in mm"),
        'volume_auto': fields.boolean('Auto calculate volume by sizes'),
    }

    _defaults = {
        'volume_auto': lambda *a: True,
    }

    def onchange_sizes(self, cr, uid, ids, width, height, depth, volume_auto):
        if volume_auto and width>0 and height>0 and depth>0:
            v = {}
            v['volume'] = width * height * depth / 1000000000.0
            print v['volume']
            return {'value': v}
        else:
            return {}
product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: