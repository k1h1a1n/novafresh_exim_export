from odoo import models,api
import logging


class IgmCustomReport(models.AbstractModel):
    _name = 'report.exim.igm_report_template'
    _description = 'IGM Custom Report'

    # @api.model
    # def _get_report_values(self, docids, data=None):
    #     docs1 = self.env['exim.shipments.igm'].sudo().browse(docids)
    #     _logger.info("Access "+str(docs1))

        # packing = 0
        # for i in docs1.invoice_line_ids:
        # packing = packing + i.packing
        
        # _logger.info("Pacxking "+str(packing))

        # net_wt = 0
        # for i in docs1.invoice_line_ids:
        #     net_wt = net_wt + i.quantity

        # gross_wt = 0
        # for i in docs1.invoice_line_ids:
        #     gross_wt = gross_wt + i.gross_wt

        # packings = [{
        #     'packing': str(packing),
        #     'net_wt': str(net_wt),
        #     'gross_wt': str(gross_wt),
        # }]
        # return {
        #       'doc_ids': docids,
        #       'doc_model': 'exim.shipments.igm',
        #       'data': docs1
        # }