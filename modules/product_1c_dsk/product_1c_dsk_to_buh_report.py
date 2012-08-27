#coding: utf-8
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
from osv import osv
from report.interface import report_int
from xml.dom.minidom import Document
from tools.translate import _

class product_1c_dsk_to_buh_report(report_int):
    def create(self, cr, uid, ids, datas, context=None):
        if context is None:
            context = {}

        doc = Document()
        xmlData = doc.createElement('data')
        doc.appendChild(xmlData)
        xmlProducts = doc.createElement('products')
        xmlData.appendChild(xmlProducts)

        pool = pooler.get_pool(cr.dbname)
        product_ids = pool.get('product.product').search(cr, uid, [], context=context)
        for product_id in product_ids:
            product = pool.get('product.product').browse(cr, uid, product_id, context)

            xmlProduct = doc.createElement('product')
            xmlProduct.setAttribute('id', str(product_id))
            if product.code_1c_buh:
                xmlProduct.setAttribute('id_buh', product.code_1c_buh)

            xmlProductName = doc.createElement('name')
            xmlProductNameText = doc.createTextNode(product.name)
            xmlProductName.appendChild(xmlProductNameText)
            xmlProduct.appendChild(xmlProductName)

            vat = 0
            for tax in product.taxes_id:
                if tax.description == 'vat':
                    vat = int(tax.amount * 100)
                    break
            if not vat:
                raise osv.except_osv(_('Every product must have vat tax!'), _('Add vat tax to the product: ') + product.name)
            xmlProductVat = doc.createElement('vat')
            xmlProductVatText = doc.createTextNode(str(vat))
            xmlProductVat.appendChild(xmlProductVatText)
            xmlProduct.appendChild(xmlProductVat)

            xmlProductUom = doc.createElement('uom')
            xmlProductUomText = doc.createTextNode(product.uom_id.name)
            xmlProductUom.appendChild(xmlProductUomText)
            xmlProduct.appendChild(xmlProductUom)

            xmlProducts.appendChild(xmlProduct)
        return (doc.toprettyxml(indent='  ', encoding='UTF-8'), 'xml')
product_1c_dsk_to_buh_report('report.product_1c_dsk_to_buh_report')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: