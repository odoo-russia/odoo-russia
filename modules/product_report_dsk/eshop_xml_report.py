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

import pooler
from report.interface import report_int
from xml.dom.minidom import Document
from datetime import datetime

class eshop_xml_report(report_int):
    def create(self, cr, uid, ids, datas, context=None):
        if context is None:
            context = {}

        doc = Document()
        xmlCatalog = doc.createElement('catalog')
        xmlCatalog.setAttribute('date', datetime.now().strftime('%Y-%m-%d %H:%M'))
        doc.appendChild(xmlCatalog)

        categories = []
        xmlCategories = doc.createElement('categories')
        xmlCatalog.appendChild(xmlCategories)

        product_types = []
        params = []
        xmlProductTypes = doc.createElement('product_types')
        xmlCatalog.appendChild(xmlProductTypes)

        brands = []
        xmlBrands = doc.createElement('brands')
        xmlCatalog.appendChild(xmlBrands)

        countries = []
        xmlCountries = doc.createElement('countries')
        xmlCatalog.appendChild(xmlCountries)

        xmlProducts = doc.createElement('products')
        xmlCatalog.appendChild(xmlProducts)

        pool = pooler.get_pool(cr.dbname)
        product_ids = pool.get('product.product').search(cr, uid, [], context=context)
        products = pool.get('product.product').browse(cr, uid, product_ids, context)
        for product in products:
            if product.categ_id and product.attribute_group and product.manufacturer_ids \
                and product.manufacturer_ids[0] and product.manufacturer_ids[0].product_brand_id:

                manufacturer = product.manufacturer_ids[0]
                brand = {
                    'id': manufacturer.product_brand_id.id,
                    'name': manufacturer.product_brand_id.name,
                    'description': manufacturer.product_brand_id.description
                }
                if brand not in brands:
                    brands.append(brand)
                    xmlBrand = doc.createElement('brand')
                    xmlBrand.setAttribute('id', str(brand['id']))
                    xmlBrands.appendChild(xmlBrand)
                    xmlBrandName = doc.createElement('name')
                    xmlBrand.appendChild(xmlBrandName)
                    xmlText = doc.createTextNode(brand['name'])
                    xmlBrandName.appendChild(xmlText)
                    xmlBrandDesc = doc.createElement('description')
                    xmlBrand.appendChild(xmlBrandDesc)
                    if brand['description']:
                        xmlText = doc.createTextNode(brand['description'])
                        xmlBrandDesc.appendChild(xmlText)

                category = {'id': product.categ_id.id, 'name': product.categ_id.name}
                if category not in categories:
                    categories.append(category)
                    xmlCategory = doc.createElement('category')
                    xmlCategory.setAttribute('id', str(category['id']))
                    xmlCategories.appendChild(xmlCategory)
                    xmlText = doc.createTextNode(category['name'])
                    xmlCategory.appendChild(xmlText)

                product_type = {
                    'id': product.attribute_group.id,
                    'name': product.attribute_group.name,
                    'link': product.attribute_group
                }
                if product_type not in product_types:
                    product_types.append(product_type)
            else:
                #TODO insert logger here
                continue

            xmlProduct = doc.createElement('product')
            xmlProduct.setAttribute('id', str(product.id))
            xmlProduct.setAttribute('category_id', str(category['id']))
            xmlProduct.setAttribute('product_type_id', str(product_type['id']))
            xmlProduct.setAttribute('brand_id', str(manufacturer.product_brand_id.id))

            xmlProductName = doc.createElement('name')
            xmlProduct.appendChild(xmlProductName)
            xmlText = doc.createTextNode(product.name)
            xmlProductName.appendChild(xmlText)

            xmlProductShortDesc = doc.createElement('description_short')
            xmlProduct.appendChild(xmlProductShortDesc)
            if product.description_short:
                xmlText = doc.createTextNode(product.description_short)
                xmlProductShortDesc.appendChild(xmlText)

            xmlProductDesc = doc.createElement('description')
            xmlProduct.appendChild(xmlProductDesc)
            if product.description:
                xmlText = doc.createTextNode(product.description)
                xmlProductDesc.appendChild(xmlText)

            xmlProductCountry = doc.createElement('country')
            xmlProduct.appendChild(xmlProductCountry)

            if manufacturer.product_country_id:
                country = {'id': manufacturer.product_country_id.id, 'name': manufacturer.product_country_id.name}
                if country not in countries:
                    countries.append(country)
                    xmlCountry = doc.createElement('country')
                    xmlCountry.setAttribute('id', str(country['id']))
                    xmlCountries.appendChild(xmlCountry)
                    xmlText = doc.createTextNode(country['name'])
                    xmlCountry.appendChild(xmlText)
                xmlText = doc.createTextNode(str(manufacturer.product_country_id.id))
                xmlProductCountry.appendChild(xmlText)
                
            xmlProductPrice = doc.createElement('price')
            xmlProduct.appendChild(xmlProductPrice)
            #TODO Insert real price here
            xmlText = doc.createTextNode('1000')
            xmlProductPrice.appendChild(xmlText)

            xmlProductStock = doc.createElement('stock')
            xmlProduct.appendChild(xmlProductStock)
            #TODO Insert real stock here
            xmlText = doc.createTextNode('1')
            xmlProductStock.appendChild(xmlText)

            xmlProductWidth = doc.createElement('width')
            xmlProduct.appendChild(xmlProductWidth)
            xmlText = doc.createTextNode(str(product.width))
            xmlProductWidth.appendChild(xmlText)

            xmlProductHeight = doc.createElement('height')
            xmlProduct.appendChild(xmlProductHeight)
            xmlText = doc.createTextNode(str(product.height))
            xmlProductHeight.appendChild(xmlText)

            xmlProductDepth = doc.createElement('depth')
            xmlProduct.appendChild(xmlProductDepth)
            xmlText = doc.createTextNode(str(product.depth))
            xmlProductDepth.appendChild(xmlText)

            xmlProductWeight = doc.createElement('weight')
            xmlProduct.appendChild(xmlProductWeight)
            xmlText = doc.createTextNode(str(product.weight))
            xmlProductWeight.appendChild(xmlText)

            xmlProductVolume = doc.createElement('volume')
            xmlProduct.appendChild(xmlProductVolume)
            xmlText = doc.createTextNode(str(product.volume))
            xmlProductVolume.appendChild(xmlText)

            xmlProductParams = doc.createElement('params')
            xmlProduct.appendChild(xmlProductParams)

            for product_avp in product.attribute_value_product_ids:
                if product_avp.attribute_id.id not in params:
                    params.append(product_avp.attribute_id.id)
                xmlProductParam = doc.createElement('param')
                xmlProductParam.setAttribute('id', str(product_avp.attribute_id.id))
                xmlProductParams.appendChild(xmlProductParam)
                if product_avp.attribute_value_id.name:
                    xmlText = doc.createTextNode(product_avp.attribute_value_id.name)
                    xmlProductParam.appendChild(xmlText)
            
            xmlProducts.appendChild(xmlProduct)
        if product_types:
            xmlParams = doc.createElement('params')
            xmlCatalog.insertBefore(xmlParams, xmlProductTypes)
            attribute_ids = pool.get('product.attribute').search(cr, uid, [], context=context)
            attributes = pool.get('product.attribute').browse(cr, uid, attribute_ids, context)
            for attribute in attributes:
                if attribute.id in params:
                    xmlParam = doc.createElement('param')
                    xmlParam.setAttribute('id', str(attribute.id))
                    xmlParams.appendChild(xmlParam)
                    xmlText = doc.createTextNode(attribute.name)
                    xmlParam.appendChild(xmlText)
            for product_type in product_types:
                xmlProductType = doc.createElement('product_type')
                xmlProductType.setAttribute('id', str(product_type['id']))
                xmlProductTypes.appendChild(xmlProductType)

                xmlProductTypeName = doc.createElement('name')
                xmlProductType.appendChild(xmlProductTypeName)
                xmlText = doc.createTextNode(product_type['name'])
                xmlProductTypeName.appendChild(xmlText)

                xmlProductTypeParams = doc.createElement('params')
                xmlProductType.appendChild(xmlProductTypeParams)

                for param in product_type['link'].attribute_ids:
                    if param.id in params:
                        xmlProductTypeParam = doc.createElement('param')
                        xmlProductTypeParams.appendChild(xmlProductTypeParam)
                        xmlText = doc.createTextNode(str(param.id))
                        xmlProductTypeParam.appendChild(xmlText)
        return (doc.toprettyxml(indent='  ', encoding='UTF-8'), 'txt')
eshop_xml_report('report.eshop_xml_report')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: