from odoo import models, fields , api
import logging

_logger = logging.getLogger(__name__)

class EximProduct(models.Model):
    _inherit = 'product.template'
    hsn_code = fields.Char(string="HSN Code")
    prefix =  fields.Char(string="Prefix", required=True)
    duty_bcd_percentage = fields.Float(string="Duty (BCD)")
    duty_sws_percentage = fields.Float(string="Duty (SWS)")
    duty_aidc_percentage = fields.Float(string="Duty (AIDC)")
    duty_gst_percentage = fields.Float(string="Duty (GST)")