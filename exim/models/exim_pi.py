from odoo import models, fields ,api
import logging

_logger = logging.getLogger(__name__)

class EximProformaInvoice(models.Model):
    _name = 'exim.pi'
    _inherit = ['mail.thread']
    _description = "Proforma Invoice"
    _rec_name = 'pi_no'
    pi_no = fields.Char(string="PI No.", required = True)
    ref_no = fields.Char(string="Reference No.")
    consignee_name = fields.Many2one('res.partner', string="Consignee", required=True)
    shipper_name = fields.Many2one('res.partner',string="Shipper", required=True)
    product_details = fields.One2many('exim.pi.product','pi_id',string="Product Detail",required=True)
    payment_terms = fields.Text("Payment Terms")
    incoterms =  fields.Selection([('cif', 'CIF'),('fob', 'FOB'),('cnf', 'CNF')],default="cif", string='Incoterms')
    shipment_count = fields.Integer(compute="_compute_shipment_count")
    currency_id = fields.Many2one('res.currency',compute='_compute_currency',string='Currency' ,required=True)
    state = fields.Selection([('draft', 'Draft'),('inprogress', 'In-Progress'),('complete', 'Complete')],default="draft", string='State')
    amount_total = fields.Monetary('Total',compute='_compute_total_amount', currency_field='currency_id', required=True) 
    # discount = fields.Monetary('Discount', currency_field='currency_id', required=True)
    # final_amount = fields.Monetary("Final Amount",compute='_compute_final_amount', currency_field='currency_id')
    port_of_embarkation = fields.Many2one('configuration.port.child',string="Port of Embarkation",required=True,domain="[('parent_field_id', '=', country_of_origin)]")
    country_of_origin = fields.Many2one('configuration.port.parent',string="Country of Origin",required=True)
    port_of_discharge = fields.Many2one('configuration.port.child',string="Port of Discharge",required=True,domain="[('parent_field_id', '=', country_of_destination)]")
    country_of_destination = fields.Many2one('configuration.port.parent',string="Country of Destination",required=True)
    active = fields.Boolean(string="Active",default=True)


    @api.onchange("consignee_name")
    def set_domain_for_consignee(self):
        category = self.env['res.partner.category'].search([('name', '=','Consignee' )])
        partner_id = []
        for i in category.partner_ids:
            partner_id.append(i.id)
            _logger.info( "Consignee : " + str(i.id))


        result = { 
                    'domain': {'consignee_name': [ 
                    ('id', 'in', partner_id)] 
                    } 
                 } 
        return result
    
    @api.onchange("shipper_name")
    def set_domain_for_shipper_name(self):
        category = self.env['res.partner.category'].search([('name', '=','Shipper' )])
        partner_id = []
        for i in category.partner_ids:
            partner_id.append(i.id)
            _logger.info( "Consignee : " + str(i.id))
        result = { 
                    'domain': {'shipper_name': [ 
                    ('id', 'in', partner_id)] 
                    } 
                 } 
        return result


    @api.depends('shipper_name')
    def _compute_currency(self):
        for pi in self:
            if pi.shipper_name:
                pi.currency_id = pi.shipper_name.country_id.currency_id
            else:
                pi.currency_id = None
    
    # @api.depends('discount')
    # def _compute_final_amount(self):
    #     for pi in self:
            # pi.final_amount = pi.amount_total - pi.discount
    
    @api.depends('product_details')
    def _compute_total_amount(self):
        for pi in self:
            sum = 0
            for product_detail in pi.product_details:
                sum = sum + product_detail.total
            pi.amount_total = sum
        
    def _compute_shipment_count(self):
        Shipment = self.env['exim.shipments']
        for pi in self:
            pi.shipment_count = Shipment.search_count([('pi_no_id','=',pi.id)])
    
    def button_confirm(self):
        self.write({'state': 'inprogress' })

    def button_close(self):
        self.write({'state': 'complete' })
    
    def button_open(self):
        self.write({'state': 'inprogress' })
    
class EximProformaInvoiceProduct(models.Model):
    _name = 'exim.pi.product'
    product_id = fields.Many2one('product.template',string="Product", required=True)
    uom_id = fields.Many2one('uom.uom',string="UoM", required=True)
    qty = fields.Float('Net Wt', required=True)
    net_wt = fields.Float('Quantity', required=True)
    price = fields.Monetary( 'Price' ,currency_field='currency_id', required=True)
    # discount = fields.Monetary( 'Discount', currency_field='currency_id', required=True)
    grade = fields.Char(string="Grade")
    total = fields.Monetary(string='Total', currency_field='currency_id',compute='_compute_total',required=True) 
    currency_id = fields.Many2one('res.currency',compute='_compute_currency', inverse='_set_uom',string='Currency' ,required=True)
    pi_id = fields.Many2one('exim.pi', string="Parent ID")
    def _set_uom(self):
        pass

    # @api.depends('discount','net_wt')
    # def _compute_price(self):
    #     try:
    #         for product in self:
    #             product.price = product.discount / product.net_wt
    #     except:
    #         product.price = 0

    @api.depends('qty','price')
    def _compute_total(self):
        for product in self:
            if product.price:
                total_price = product.price * product.qty
                product.total = total_price
            else:
                product.total = 0
    
    @api.depends('pi_id')
    def _compute_currency(self):
        for product in self:
            if product.pi_id.shipper_name:
                product.currency_id = product.pi_id.shipper_name.country_id.currency_id
            else:
                product.currency_id = None
    





