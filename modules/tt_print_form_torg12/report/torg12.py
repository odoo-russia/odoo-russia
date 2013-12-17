from openerp.report import report_sxw
import time


class torg12_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(torg12_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time})

report_sxw.report_sxw('report.account.invoice.torg12', 'account.invoice',
                      'tt_print_form_torg12/torg12.jrxml',
                      parser=torg12_report)