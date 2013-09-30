{
    'name' : 'Schet Factura Print Form',
    'version' : '1.0',
    'category' : 'Extra Reports',
    'author'  : 'Transparent Technologies',
    'license' : 'AGPL-3',
    'depends' : ['base',
                 'jasper_reports',
                 'l10n_ru',
                 'account',
                 'tt_acc_invoice_line_subtotal_gross',
                 'tt_print_forms_names',],
    'update_xml' : ['invoice_form_data.xml',],
    'installable': True,
    'auto_install': False,
    'description': '''
This module adds Invoice Print Form.
============================================================
    '''
}