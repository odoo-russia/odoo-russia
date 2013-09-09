#!/usr/bin/python

# OKEI Parser
# Input file format:
#     <okei_code>\t<full_name>\t<name>

header = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
header1 = "<openerp>\n"
header2 = "\t<data noupdate=\"0\">\n"
footer2 = "\t</data>\n"
footer1 = "</openerp>\n"


def format_category(name, count):
    return """
\t\t<record id="product_uom_categ_%s" model="product.uom.categ">
\t\t\t<field name="name">%s</field>
\t\t</record>
""" % (count, name)


def format_uom(count_uom, count_category, full_name, name, okei):
    return """
\t\t\t<record id="product_uom_%s" model="product.uom">
\t\t\t\t<field name="category_id" ref="product_uom_categ_%s"/>
\t\t\t\t<field name="name">%s.</field>
\t\t\t\t<field name="full_name">%s</field>
\t\t\t\t<field name="okei">%s</field>
\t\t\t\t<field name="factor">1</field>
\t\t\t</record>
""" % (count_uom, count_category, name, full_name, okei)

print 'Opening file...'
try:
    file = open('okei', 'r', False)
    file_out = open('product_uom_data.xml', 'w')

    print 'Parsing...'
    file_out.write(header)
    file_out.write(header1)
    file_out.write(header2)

    res = {}
    key = ''
    category_count = 0
    for line in file:
        line.replace('\n', '')
        values = line.split('\t')
        if len(values) > 1:
            if not values[2]:
                values[2] = values[1]
            if not values[0]:
                print 'Somethings wrong'
            res[key].append({
                'full_name': values[1],
                'okei': values[0],
                'name': values[2],
            })
        else:
            key = values[0].replace('\n', '')
            if key not in res:
                res[key] = []

    count_category= 0
    count_uom= 0
    for key in res.keys():
        file_out.write("\n\t\t<!-- Product UOM: %s -->"%key)
        file_out.write(format_category(key, count_category))
        for value in res[key]:
            file_out.write(format_uom(count_uom, count_category, value['full_name'], value['name'], value['okei']))
            count_uom += 1
        count_category += 1
        #     print "\t%s [%s][%s]"%(value['full_name'], value['okei'], value['code1'])

    file_out.write(footer2)
    file_out.write(footer1)
    print 'Ready!'
except Exception as ex:
    print ex.message
