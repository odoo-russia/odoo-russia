#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Генерация справочника банков

import os
from lxml import etree

OUT_FILE = os.path.join(os.path.dirname(__file__), '../../data/res_bank_data.xml')


def generate_bank_file(out_file):
    bic_list = utils.get_bic_list()

    def _append_field(name, text):
        if not name:
            name = chr(32)
        n = etree.SubElement(record, 'field', attrib={'name': name})
        n.text = text

    root = etree.Element('openerp')
    data = etree.SubElement(root, 'data', attrib={'noupdate': '0'})

    for bic in bic_list.values():
        record = etree.SubElement(data, 'record',
                                  attrib={'model': 'res.bank',
                                          'id': '%s' % bic['bic']})
        for k, v in bic.items():
            _append_field(k, v)
        etree.SubElement(record, 'field', attrib={'model': 'res.country',
                                                  'name': 'country',
                                                  'ref': 'base.ru'})
    with open(out_file, 'wb') as f:
        f.write(etree.tostring(root,
                               pretty_print=True,
                               xml_declaration=True,
                               encoding='utf-8'))


if __name__ == '__main__':
    # поправим sys.path чтобы можно было подключить модуль
    os.sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                    '..', '..', '..')))
    from l10n_ru import utils
    generate_bank_file(OUT_FILE)
