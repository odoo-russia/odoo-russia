from openerp.report import report_sxw
import time


class bill_of_product_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(bill_of_product_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time})

report_sxw.report_sxw('report.account.invoice.nakl_sklad', 'account.invoice',
                      'tt_print_form_nakl_sklad/nakl_sklad.jrxml',
                      parser=bill_of_product_report)