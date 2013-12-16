from openerp.report import report_sxw
import time


class schet_sale_order_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(schet_sale_order_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time})

report_sxw.report_sxw('report.sale.order.schet', 'sale.order',
                      'tt_print_form_schet/schet.jrxml',
                      parser=schet_sale_order_report)