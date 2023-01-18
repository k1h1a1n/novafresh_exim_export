from odoo import models, fields ,api
from odoo.exceptions import ValidationError
import logging
from datetime import datetime, timedelta


_logger = logging.getLogger(__name__)

class ExportInvoiceDBK(models.Model):
    _name = 'export.invoice.dbk'
    _inherit=['mail.thread','mail.activity.mixin']
    _description = "DBK"
    _rec_name = "sb_no" 
    bank_inward_no = fields.Char(string="BANK INWARD NO")
    so_id = fields.Many2one('sale.order',string="Sales Order",required=True)
    consignee = fields.Many2one("res.partner",string="Consignee")
    export_lot = fields.Many2one('export.lot',string="Lot",required=True)
    account_move_id = fields.Many2one('account.move',string="Invoice")
    home_currency = fields.Many2one('res.currency', string="Home Currency")
    foreign_currency = fields.Many2one('res.currency', string="Foreign Currency")
    ex_rate = fields.Monetary("Exchange Rate",currency_field="home_currency")
    date = fields.Date(string="Date")
    product_details = fields.One2many('export.invoice.dbk.product','dbk_id',string="Product Detail",required=True)
    total_invoice_foreign_currency = fields.Monetary("Total Invoice CIF Foreign",currency_field="foreign_currency",compute="_compute_cif")
    total_invoice_home_currency = fields.Monetary("Total Invoice CIF Home",compute="_compute_ex_rate",currency_field="home_currency")

    freight = fields.Monetary("Freight",currency_field="foreign_currency")
    fob_value_foreign = fields.Monetary("Fob Value Foreign",currency_field="foreign_currency",compute="_compute_fob_value_foreign")
    fob_value_home = fields.Monetary("Fob Value HOME",compute="_compute_ex_rate",currency_field="home_currency")

    #Shipping
    sb_no = fields.Char("Shipping Bill")
    sb_date = fields.Date("Shipping Bill Date")
    sb_port = fields.Many2one("configuration.port.child",string="Port")

    #RODTEP
    rodtep = fields.Monetary("RODTEP Amount",currency_field="home_currency")
    rodtep_received = fields.Monetary("RODTEP Recieved",currency_field="home_currency")
    rodtep_status = fields.Selection([('pending', 'Pending'),('received', 'Received')],default='pending',string='RODTEP Status')
    rodtep_scroll_no = fields.Char("RODTEP Scroll No.")
    rodtep_scroll_date = fields.Date("RODTEP Scroll Date")
    rodtep_e_script = fields.Char("RODTEP e Script")
    rodtep_bill_no = fields.Char("RODTEP Bill No.")

    #DBK
    dbk = fields.Monetary("DBK Amount",currency_field="home_currency")
    dbk_received = fields.Monetary("DBK Recieved",currency_field="home_currency")
    dbk_pending = fields.Monetary("DBK Pending",currency_field="home_currency")
    dbk_status = fields.Selection([('pending', 'Pending'),('received', 'Received')],default='pending',string='DBK Status')
    dbk_scroll_no = fields.Char("DBK Scroll No.")
    dbk_scroll_date = fields.Date("DBK Scroll Date")

    #BRC
    value_brc =  fields.Monetary("Value As per BRC",currency_field="home_currency")
    brc_no = fields.Char("BRC No.")
    brc_date = fields.Date("BRC Date")
    brc_status = fields.Selection([('pending', 'Pending'),('issued', 'Issued')],default='pending',string='eBRC Status')

    egm_no = fields.Char("EGM No.")
    egm_date = fields.Date("EGM Date.")
    tma = fields.Integer("TMA")
    customs_file_name = fields.Char(string="Customs File Name")

    @api.depends("freight","total_invoice_foreign_currency")
    def _compute_fob_value_foreign(self):
        for record in self:
            record.fob_value_foreign = record.total_invoice_foreign_currency - record.freight
            

    @api.depends("product_details.amount")
    def _compute_cif(self):
        for record in self:
            sum = 0
            for product_detail  in record.product_details:
                sum = sum + product_detail.amount
            record.total_invoice_foreign_currency = sum
 

    @api.onchange("export_lot")
    def set_field(self):
        _logger.info("SAS" +str(len(self.export_lot)))

        if len(self.export_lot)>0:
           
            self.sb_port = self.export_lot.ports

        else:
            pass

    @api.onchange("export_lot")
    def set_domain_for_lot(self):
        if not self.so_id:
            raise ValidationError("Please Select Sales Order First")
        else:
            lot_ids=[]
            lot = self.env['export.lot']
            lots = lot.search([('so_id','=', self.so_id.id)])
            for lot in lots:
                lot_ids.append(lot.id)
            result = { 
                    'domain': {'export_lot': [ 
                    ('id', 'in', lot_ids)] 
                    } 
                 } 
            return result


    @api.model
    def default_get(self, fields_list):
       res = super(ExportInvoiceDBK, self).default_get(fields_list)
       vals = []
       _logger.info("Working " + str(res))
       if res:
        invoice = self.env['account.move'].search([('id', '=', res["account_move_id"] )])
        products = invoice.invoice_line_ids
        currency = invoice.currency_id
        for i in products:
            if not i.product_id.id:
                continue
            else:
                _logger.info("Prod " + str(i.product_id))
                data = (0, 0, {'product': i.product_id.id,'foreign_currency':currency,'net_wt':i.quantity,'gross_wt':i.gross_wt,'box_crate':i.packing,'rate_per_kg':i.price_unit,'amount':i.price_subtotal })
                vals.append(data)
        _logger.info("vals " + str(vals))
        res.update({'product_details': vals,'foreign_currency':currency })
       return res
    

    @api.depends("ex_rate","fob_value_foreign","total_invoice_foreign_currency")
    def _compute_ex_rate(self):
        self.total_invoice_home_currency = self.ex_rate * self.total_invoice_foreign_currency
        self.fob_value_home = self.ex_rate * self.fob_value_foreign
        



class ExportInvoiceDBKProduct(models.Model):
    _name = 'export.invoice.dbk.product'
    dbk_id = fields.Many2one('export.invoice.dbk',string="DBK")
    foreign_currency = fields.Many2one('res.currency', string="Foreign Currency")
    product = fields.Many2one('product.product',"Product",required=True)
    box_crate = fields.Integer("Box/Crate")
    net_wt = fields.Integer("Net Wt.")
    gross_wt = fields.Integer("Gross Wt.")
    rate_per_kg = fields.Monetary("Rate Per Kg",currency_field="foreign_currency")
    amount = fields.Monetary("Amount",currency_field="foreign_currency")
   

  

    


