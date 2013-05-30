# -*- coding: utf-8 -*-

import time
from openerp.report import report_sxw

class acc_inv(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(acc_inv, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {'time': time,})

report_sxw.report_sxw('report.new_report', 'account.invoice',
                      'account_invoice_print_form/Akt.jrxml',
                      parser=acc_inv)
