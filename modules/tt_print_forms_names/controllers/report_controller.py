# coding: utf-8
import simplejson
import time
import base64
import zlib
import openerp.addons.web.controllers.main as main
from openerp.addons.web import http as http
openerpweb = http


class Reports(openerpweb.Controller):
    _cp_path = "/web/named_report"
    POLLING_DELAY = 0.25
    TYPES_MAPPING = {
        'doc': 'application/vnd.ms-word',
        'html': 'text/html',
        'odt': 'application/vnd.oasis.opendocument.text',
        'pdf': 'application/pdf',
        'sxw': 'application/vnd.sun.xml.writer',
        'xls': 'application/vnd.ms-excel',
    }

    def _get_file_name(self, request, model, report_name, context):
        model_obj = request.session.model(model)
        field_number = ""
        field_date = ""
        file_name = ""
        if model == 'account.invoice':
            field_date = 'date_invoice'
            field_number = 'number_only'
        elif model == 'sale.order':
            field_date = 'date_order'
            field_number = 'number_only'
        elif model.startswith('stock.picking'):
            field_date = 'date'
            field_number = 'name'

        if field_date and field_number:
            model_data = model_obj.read(context['active_id'], [field_number, field_date, 'partner_id'], context)
            report_number = u"№" + model_data[field_number] if model_data[field_number] else ""
            report_date = u"от " + model_data[field_date] if model_data[field_date] else ""
            report_partner_name = u"для " + model_data['partner_id'][1] if model_data['partner_id'] else ""
            file_name = u"%s %s %s %s" % (report_name, report_number, report_date, report_partner_name)

        return file_name

    @openerpweb.httprequest
    def index(self, req, action, token):
        action = simplejson.loads(action)

        report_srv = req.session.proxy("report")
        context = dict(req.context)
        context.update(action["context"])

        report_data = {}
        report_ids = context["active_ids"]
        if 'report_type' in action:
            report_data['report_type'] = action['report_type']
        if 'datas' in action:
            if 'ids' in action['datas']:
                report_ids = action['datas'].pop('ids')
            report_data.update(action['datas'])

        report_id = report_srv.report(
            req.session._db, req.session._uid, req.session._password,
            action["report_name"], report_ids,
            report_data, context)

        report_struct = None
        while True:
            report_struct = report_srv.report_get(
                req.session._db, req.session._uid, req.session._password, report_id)
            if report_struct["state"]:
                break

            time.sleep(self.POLLING_DELAY)

        report = base64.b64decode(report_struct['result'])
        if report_struct.get('code') == 'zlib':
            report = zlib.decompress(report)
        report_mimetype = self.TYPES_MAPPING.get(
            report_struct['format'], 'octet-stream')

        model = report_data.get('model')
        if not model:
            model = context.get('active_model')

        report_name = action.get('name', 'report')
        if 'name' not in action:
            reports = req.session.model('ir.actions.report.xml')
            res_id = reports.search([('report_name', '=', action['report_name']),],
                                    0, False, False, context)
            if len(res_id) > 0:
                if res_id > 1:
                    res_id[0] = res_id[1]
                report_name = reports.read(res_id[0], ['name'], context)['name']
            else:
                report_name = action['report_name']

        file_name = self._get_file_name(req, model, report_name, context)

        return req.make_response(report,
             headers=[
                 ('Content-Disposition', main.content_disposition(file_name, req)),
                 ('Content-Type', report_mimetype),
                 ('Content-Length', len(report))],
             cookies={'fileToken': token})