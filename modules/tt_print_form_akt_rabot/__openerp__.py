{
    'name' : 'Akt vypolnennykh rabot',
    'version' : '1.0',
    'category' : 'Extra Reports',
    'author'  : 'Transparent Technologies Ltd.',
    'license' : 'AGPL-3',
    'depends' : ['base',
                 'jasper_reports',
                 'l10n_ru',
                 'tt_acc_invoice_line_subtotal_gross',
                 'tt_print_forms_names',],
    'update_xml' : ['acc_inv_data.xml',],
    'installable': True,
    'auto_install': False,
    'description': '''
This module adds Account Invoice Print Form.
============================================================
    '''
}