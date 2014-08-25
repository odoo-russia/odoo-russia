{
    'name' : 'Schet Print Form',
    'version' : '1.0',
    'category' : 'Extra Reports',
    'author'  : 'Transparent Technologies Ltd.',
    'license' : 'AGPL-3',
    'depends' : ['base',
                 'sale',
                 'account',
                 'jasper_reports',
                 'l10n_ru',
                 'tt_acc_invoice_line_subtotal_gross',
                 'tt_sale_order_line_subtotal_gross',
                 'tt_print_forms_names',],
    'update_xml' : ['sale_order_data.xml',],
    'installable': True,
    'auto_install': False,
    'description': '''
This module adds new Sale Order Print Form.
============================================================
    '''
}