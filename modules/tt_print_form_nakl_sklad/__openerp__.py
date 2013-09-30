{
    'name' : 'Bill of product print form',
    'version' : '1.0',
    'category' : 'Extra Reports',
    'author'  : 'Transparent Technologies',
    'license' : 'AGPL-3',
    'depends' : ['base',
                 'account',
                 'jasper_reports',
                 'l10n_ru',
                 'tt_acc_invoice_line_subtotal_gross',
                 'tt_print_forms_names',],
    'update_xml' : ['bill_of_product_form_data.xml',],
    'installable': True,
    'auto_install': False,
    'description': '''
This module adds new Bill of product form
============================================================
    '''
}