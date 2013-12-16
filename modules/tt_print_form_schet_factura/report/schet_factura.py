from openerp.report import report_sxw
import time


class schet_factura_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(schet_factura_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time})

report_sxw.report_sxw('report.account.invoice.schet_factura', 'account.invoice',
                      'tt_print_form_schet_factura/schet_factura.jrxml',
                      parser=schet_factura_report)