#########################################################################
# Copyright (C) 2009  Sharoon Thomas, Open Labs Business solutions      #
#                                                                       #
#This program is free software: you can redistribute it and/or modify   #
#it under the terms of the GNU General Public License as published by   #
#the Free Software Foundation, either version 3 of the License, or      #
#(at your option) any later version.                                    #
#                                                                       #
#This program is distributed in the hope that it will be useful,        #
#but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#GNU General Public License for more details.                           #
#                                                                       #
#You should have received a copy of the GNU General Public License      #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#########################################################################
from osv import osv,fields

class product_product(osv.osv):
    def images_count(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        res = {}
        for product in self.browse(cr, uid, ids, context=context):
            if product.image_ids:
                count = 0
                for product_image in product.image_ids:
                    if product_image.type == 'image':
                        count += 1
                res[product.id] = count
            else:
                res[product.id] = 0
        return res

    def schemes_count(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        res = {}
        for product in self.browse(cr, uid, ids, context=context):
            if product.image_ids:
                count = 0
                for product_image in product.image_ids:
                    if product_image.type == 'scheme':
                        count += 1
                res[product.id] = count
            else:
                res[product.id] = 0
        return res

    _name = "product.product"
    _inherit = "product.product"
    _columns = {
        'image_ids': fields.one2many(
                'product.images',
                'product_id',
                'Product Images'
        ),
        'images_count': fields.function(images_count, type='integer', store=False, string='Images'),
        'schemes_count': fields.function(schemes_count, type='integer', store=False, string='Schemes'),
    }
product_product()