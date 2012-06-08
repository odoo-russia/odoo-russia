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
{
    "name" : "E-Shop",
    "version" : "1.0",
    "author" : "Denis Karataev",
    "category" : "E-Shop",
    "depends" : [
        "eshop_base_dsk",
        "eshop_report_dsk",
        "product",
        "product_attribute_dsk",
        "product_category_flags_dsk",
        "product_competitor_price_dsk",
        "product_description_dsk",
        "product_flags_dsk",
        "product_images_dsk",
        "product_manufacturer_dsk",
        "product_relations_dsk",
        "product_size_dsk",
    ],
    "init_xml" : [],
    "demo_xml" : [],
    "description": "Product additions for E-Shop",
    "update_xml" : [],
    "active": False,
    "installable": True,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
