# coding: utf-8
from openerp.osv import osv, fields


class account_invoice(osv.osv):
    _name = 'account.invoice'
    _inherit = 'account.invoice'

    def _get_origin(self, cr, uid, origin_str):
        sale_obj = self.pool.get('sale.order')
        sale_ids = sale_obj.search(cr, uid, [('name', '=', origin_str)])
        if sale_ids:
            return sale_obj.browse(cr, uid, sale_ids[0])
        else:
            return None

    def _format_inn_kpp(self, inn, kpp):
        if inn and kpp:
            res = "%s/%s" % (inn, kpp)
        elif inn:
            res = inn
        elif kpp:
            res = kpp
        else:
            res = ""
        return res

    def get_partner_info(self, cr, uid, ids, fields=None, args=None, context=None):
        if context is None:
            context = {}
        res = {}
        for i in ids:
            res[i] = {}.fromkeys(fields, "")

        for field in fields:
            for invoice in self.browse(cr, uid, ids, context=context):
                origin = self._get_origin(cr, uid, invoice.origin)
                field_splitted = field.split('_')
                field_prefix = field_splitted[0]
                field_postfix = field_splitted[-1]

                # Get correct partner by the prefix of field name
                if field_prefix == 'invoice' and origin and origin.partner_invoice_id:
                    partner = origin.partner_invoice_id
                elif field_prefix == 'shipping' and origin and origin.partner_shipping_id:
                    partner = origin.partner_shipping_id
                elif field_prefix == 'company':
                    partner = invoice.company_id.partner_id
                elif field_prefix == 'partner':
                    partner = invoice.partner_id
                else:
                    res[invoice.id][field] = ""
                    continue

                # Get information by the postfix of field name
                if field_postfix == 'name':
                    if not partner.name_official and partner.parent_id:
                        value = partner.parent_id.name_official
                    else:
                        value = partner.name
                elif field_postfix == 'address':
                    partner = partner.parent_id if partner.use_parent_address else partner
                    value = partner.address_formatted
                elif field_postfix == 'innkpp':
                    inn = partner.inn if partner.inn else partner.parent_id.inn
                    kpp = partner.kpp if partner.kpp else partner.parent_id.kpp
                    value = self._format_inn_kpp(inn, kpp)
                else:
                    method = getattr(self, "_get_" + field_postfix) or False
                    if method:
                        value = method((field_prefix, field_postfix), invoice, partner)
                    else:
                        value = ""
                res[invoice.id][field] = value
        return res

    _columns = {
        'invoice_name': fields.function(get_partner_info, type='char', store=False, multi='partner_info'),
        'invoice_address': fields.function(get_partner_info, type='char', store=False, multi='partner_info'),
        'invoice_innkpp': fields.function(get_partner_info, type='char', store=False, multi='partner_info'),
        'shipping_name': fields.function(get_partner_info, type='char', store=False, multi='partner_info'),
        'shipping_address': fields.function(get_partner_info, type='char', store=False, multi='partner_info'),
        'company_name': fields.function(get_partner_info, type='char', store=False, multi='partner_info'),
        'company_address': fields.function(get_partner_info, type='char', store=False, multi='partner_info'),
        'company_innkpp': fields.function(get_partner_info, type='char', store=False, multi='partner_info'),
        'partner_name': fields.function(get_partner_info, type='char', store=False, multi='partner_info'),
        'partner_innkpp': fields.function(get_partner_info, type='char', store=False, multi='partner_info'),
        'partner_address': fields.function(get_partner_info, type='char', store=False, multi='partner_info'),
    }

