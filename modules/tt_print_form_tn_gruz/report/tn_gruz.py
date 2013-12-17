from openerp.report import report_sxw
import time


class tn_gruz_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(tn_gruz_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time})

for suffix in ('', '.in', '.out'):
    report_sxw.report_sxw('report.stock.picking' + suffix + '.tn_gruz',
                          'stock.picking' + suffix,
                          'tt_print_form_tn_gruz/nakl_transp.jrxml',
                          parser=tn_gruz_report)