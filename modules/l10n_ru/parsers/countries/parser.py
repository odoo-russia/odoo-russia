#!/usr/bin/python
# coding: utf-8
# Countries Parser

from xmlrpclib import ServerProxy, Fault

input_file = "country"
out_file = "../../data/res_country_data.xml"
header = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
header1 = "<openerp>\n"
header2 = "\t<data noupdate=\"0\">\n"
footer2 = "\t</data>\n"
footer1 = "</openerp>\n"


def format_country_entry(id, name, code, full_name, iso):
    return """
\t\t<record id="base.%s" model="res.country">
\t\t\t<field name="name">%s</field>
\t\t\t<field name="code">%s</field>
\t\t\t<field name="full_name">%s</field>
\t\t\t<field name="numeral_code">%s</field>
\t\t</record>
    """%(id, name, code, full_name, iso)

try:
    source = open(input_file, 'r')
    dest = open(out_file, 'w')

    keys_line = source.readline()
    keys = keys_line.replace('\n', '').split('\t')

    dest.write(header)
    dest.write(header1)
    dest.write(header2)

    for line in source:
        values = line.replace('\n', '').split('\t')
        id = values[3].lower()
        code = id
        name = values[0]
        full_name = values[1] if values[1] else name
        iso = values[5]

        if id == 'gb':
            code = 'uk'

        entry = format_country_entry(id, name, code, full_name, iso)
        dest.write(entry)

    dest.write(footer2)
    dest.write(footer1)
    source.close()
    dest.close()

except Exception as ex:
    print 'Exception:',ex.message

