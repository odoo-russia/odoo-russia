{
    'name': 'Account Invoice extensions for Print Forms',
    'version': '1.0',
    'category': 'Extra Reports',
    'author': 'Transparent Technologies',
    'license': 'AGPL-3',
    'depends': ['base', 'account'],
    'installable': True,
    'auto_install': False,
    'description': '''
 To use this feature, you should define get_partner_info() function in account_invoice class:\n
    def get_partner_info(self, cr, uid, ids, fields=None, args=None, context=None):\n
        return super(account_invoice, self).get_partner_info(cr, uid, ids, fields, args, context)\n
 Field specification:\n
    '<who>_<what>': fields.function(get_partner_info, type='char', store=False, multi='partner_info'),\n
    There <who> is 'partner', 'company', 'invoice' or 'shipping'\n
          <what> is information what you want to get (for example name, address or 'inn_kpp')\n
    Also, you can define your own <what>. For example you want to get partner formatted bank info.\n
    You must create a new functional field:\n
        'partner_bankinfo': fields.function(get_partner_info, type='char', store=False, multi='partner_info'),\n
    and define function:\n
        def _get_bankinfo(self, invoice, partner):\n
            ... There is some code to format string with bank information ...\n
            return bank_info\n
    '''
}
