#!/usr/bin/python

# OKV Parser
# Input file format:
#     <code>\t<name>\t<full_name>

header = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
header1 = "<openerp>\n"
header2 = "\t<data noupdate=\"0\">\n"
footer2 = "\t</data>\n"
footer1 = "</openerp>\n"


def format_record(code_char, name, code_num):
    return """
\n\t\t<record id="base.%s" model="res.currency">
\t\t\t<field name="name">%s</field>
\t\t\t<field name="full_name">%s</field>
\t\t\t<field name="code">%s</field>
\t\t</record>
\t\t<record id="base.rate%s" model="res.currency.rate">
\t\t\t<field name="currency_id" ref="base.%s" />
\t\t\t<field eval="time.strftime('%%Y-01-01')" name="name"/>
\t\t</record>\n
"""%(code_char, code_char, name, code_num, code_char, code_char)


print 'Opening file...'
try:
    file = open('okv', 'r')
    file_out = open('okv.xml', 'w')

    print 'Parsing...'
    file_out.write(header)
    file_out.write(header1)
    file_out.write(header2)
    for line in file:
        line.replace('\n', '')
        values = line.split('\t')
        code_num = values[0]
        code_char = values[1][1:]
        name = values[2][1:]
        file_out.write(format_record(code_char, name, code_num))
    file_out.write(footer2)
    file_out.write(footer1)
    print 'Ready!'
except Exception as ex:
    print ex.message
