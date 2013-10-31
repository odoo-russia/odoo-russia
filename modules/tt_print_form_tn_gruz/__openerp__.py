{
    'name': 'Transportnaya naklandnaya',
    'version': '1.0',
    'category': 'Extra Reports',
    'author': 'Transparent Technologies',
    'license': 'AGPL-3',
    'depends': ['base', 'stock', 'jasper_reports', 'l10n_ru', 'tt_print_forms_names'],
    'update_xml': [
        'tt_print_form_tn_gruz_data.xml',
        'tt_print_form_tn_gruz_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'description': '''
    Transportnaya naklandnaya
    '''
}