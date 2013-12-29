#!/usr/bin/env python
# coding: utf-8

# Нормативный документ: Постановление Госстандарта России от 14.12.2001 N 529-ст (ред. от 04.07.2013)
# "О принятии и введении в действие Общероссийского классификатора стран мира"
# (вместе с "ОК (МК (ИСО 3166) 004-97) 025-2001...") (дата введения 01.07.2002)

import os
from lxml import etree

IN_FILE = 'country'
OUT_FILE = os.path.join(os.path.dirname(__file__), '../../data/res_country_data.xml')


def generate_countries(in_file, out_file):
    def _append_field(name, text):
        n = etree.SubElement(record, 'field', attrib={'name': name})
        n.text = text.strip().decode('utf-8')

    with open(in_file, 'r') as f:
        f.readline()  # skip header

        root = etree.Element('openerp')
        data = etree.SubElement(root, 'data', attrib={'noupdate': '0'})

        for l in f:
            if not l:
                continue
            c = l.split('\t')
            record = etree.SubElement(data, 'record',
                                      attrib={'model': 'res.country',
                                              'id': 'base.%s' % c[3].lower()})
            _append_field('name', c[0])
            _append_field('full_name', c[1] if c[1] else c[0])
            _append_field('numeral_code', c[5])

    with open(out_file, 'w') as f:
        f.write(etree.tostring(root,
                                pretty_print=True,
                                xml_declaration=True,
                                encoding='utf-8'))

if __name__ == '__main__':
    generate_countries(IN_FILE, OUT_FILE)
