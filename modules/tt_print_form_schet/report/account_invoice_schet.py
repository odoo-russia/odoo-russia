from openerp.report import report_sxw
import time


class schet_account_invoice_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(schet_account_invoice_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time})

report_sxw.report_sxw('report.account.invoice.schet', 'account.invoice',
                      'tt_print_form_schet/schet.jrxml',
                      parser=schet_account_invoice_report)