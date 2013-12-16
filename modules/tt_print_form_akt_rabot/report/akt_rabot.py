from openerp.report import report_sxw
import time


class account_invoice(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_invoice, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time})

report_sxw.report_sxw('report.account.invoice.akt_rabot', 'account.invoice',
                      'tt_print_form_akt_rabot/akt_rabot.jrxml',
                      parser=account_invoice)