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

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if 'image_ids' in vals and vals['image_ids']:
            if 'sequence' in vals['image_ids'][0][2]:
                min_sec = None
                min_index = None
                count = -1
                for image in vals['image_ids']:
                    count += 1
                    if min_sec is None:
                        min_sec = image[2]['sequence']
                        min_index = count
                    if image[2]['sequence'] < min_sec:
                        min_sec = image[2]['sequence']
                        min_index = count
                vals['image_medium'] = vals['image_ids'][min_index][2]['image']
            else:
                vals['image_medium'] = vals['image_ids'][0][2]['image']
        return super(product_product, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        res = super(product_product, self).write(cr, uid, ids, vals, context)
        if 'image_ids' in vals and vals['image_ids']:
            for product_id in ids:
                image_ids = self.pool.get('product.images').search(cr, uid, [('product_id', '=', product_id)],
                                                                   order='sequence', limit=1, context=context)
                if image_ids:
                    image = self.pool.get('product.images').browse(cr, uid, image_ids[0], context=context)
                    vals = {
                        'image_medium': image.image,
                    }
                    self.write(cr, uid, product_id, vals, context=context)
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