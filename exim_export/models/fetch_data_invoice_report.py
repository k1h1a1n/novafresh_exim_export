from odoo import models , fields,api
import logging


_logger = logging.getLogger(__name__)


class NovaFreshCustomReport(models.AbstractModel):
    _name = 'report.exim_export.novafresh_export_invoice_report_id_template'
    _description = 'NovaFresh Custom Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs1 = self.env['account.move'].sudo().browse(docids)
        _logger.info("Access "+str(docs1))

        packing = 0
        for i in docs1.invoice_line_ids:
            packing = packing + i.packing
        
        _logger.info("Pacxking "+str(packing))

        net_wt = 0
        for i in docs1.invoice_line_ids:
            net_wt = net_wt + i.quantity

        gross_wt = 0
        for i in docs1.invoice_line_ids:
            gross_wt = gross_wt + i.gross_wt

        packings = [{
            'packing': str(packing),
            'net_wt': str(net_wt),
            'gross_wt': str(gross_wt),
        }]

        
        return {
              'doc_ids': docids,
              'doc_model': 'account.move',
              'data': docs1,
              'packing': packings
        }


# class ExtendedInvoiceReport(models.Model):
#     _inherit = 'account.invoice.report'


#     def report_invoice_document(self):
#         print('hii afzal kha herer')
#         super(ExtendedInvoiceReport,self)._get_report_values()

#     def test(self , docids , data = None):
#         docs = self.env['res.partner'].browse(docids)
#         print('hii afzal kha herer')
#         return {
#             'doc_ids':docids,
#             'doc_model':'res.partner',
#             'docs' : docs,
#         }

    


# class ReportInvoiceWithoutPayment(models.AbstractModel):
#     _name = 'report.account.report_invoice'
#     _description = 'Account report without payment lines'

#     @api.model
#     def _get_report_values(self, docids, data=None):
#         docs = self.env['account.move'].browse(docids)

#         qr_code_urls = {}
#         for invoice in docs:
#             if invoice.display_qr_code:
#                 new_code_url = invoice.generate_qr_code()
#                 if new_code_url:
#                     qr_code_urls[invoice.id] = new_code_url

#         return {
#             'doc_ids': docids,
#             'doc_model': 'account.move',
#             'docs': docs,
#             'qr_code_urls': qr_code_urls,
#         }

class EditedReportInvoiceWithPayment(models.AbstractModel):
    _name = 'report.account.report_invoice_with_payments_edited'
    _description = 'Account report with payment lines '
    _inherit = 'report.account.report_invoice'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('hello .................saif..................................')
        rslt = super()._get_report_values(docids, data)
        rslt['report_type'] = data.get('report_type') if data else ''
        return rslt