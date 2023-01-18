from dataclasses import Field
from datetime import datetime, timedelta
from locale import currency
from multiprocessing import context
from operator import contains
import string
from this import d
from odoo import models, fields , api
from odoo.exceptions import ValidationError
from datetime import datetime,timedelta
import logging

_logger = logging.getLogger(__name__)

class EximShipment(models.Model):
    _name = 'exim.shipments'
    _description = "Shipment"
    _rec_name = 'shipment_no'
    _inherit=['mail.thread','mail.activity.mixin'] 
    pi_no_id = fields.Many2one('exim.pi',string='Proforma Invoice', required=True)
    year = fields.Many2one('exim.shipments.sequence',string='Year', required=True)
    consignee_name = fields.Many2one('res.partner', string="Consignee",compute="_compute_consignee",required=True,store=True)
    responsible_user = fields.Many2one('res.users','Responsible User', default=lambda self: self.env.user)
    shipment_no = fields.Char('Shipment')
    lot_no = fields.Char('Lot No.')
    shipper_id = fields.Many2one('res.partner',compute='_compute_shipper',string="Shipper",store=True)
    eta = fields.Datetime('ETA',required=True)
    etd = fields.Datetime('ETD',required=True)
    arriving_in = fields.Char("Arriving in",readonly=True,compute="_compute_arriving_time")
    arriving_in_days = fields.Integer("Arriving in days",readonly=True,compute="_compute_arriving_time")
    eta_before_fivedays = fields.Datetime('ETA Before 5 Days',compute="_compute_eta_before_five_days")
    etd_after_fivedays = fields.Datetime('ETD After 5 Days',compute="_compute_eta_before_five_days")
    cha = fields.Many2one('res.partner',string="CHA", required=True)
    container_details = fields.One2many('exim.shipments.container','shipment_id',string="Container Detail",required=True)
    commercial_invoice = fields.Many2one("exim.shipments.ci", string="Commercial Invoice")
    state = fields.Selection([('draft', 'Draft'),('confirmed', 'Confirmed'),('igm', 'IGM Received'),('released', 'Released')],default="draft", string='State') 
    carrier = fields.Many2one('res.partner',string="Carrier", required=True)
    contaiiner_nos = fields.Integer('Container Nos')
    boe_no = fields.Char("Bill of Entry No.")
    boe_date = fields.Date("BOE Date")
    coo = fields.Char(string="COO",compute="_compute_coo",store=True)
    pod = fields.Char(string="POD",compute="_compute_coo",store=True)
    phyto_file = fields.Binary(string='Phyto', attachment=True)
    phyto_file_name = fields.Char("File Name")
    phyto_required = fields.Boolean("Phyto Required")
    coo_file = fields.Binary(string='COO', attachment=True)
    coo_file_name = fields.Char("File Name")
    coo_required = fields.Boolean("COO Required")
    nongmo_file = fields.Binary(string='Non GMO', attachment=True)
    nongmo_file_name = fields.Char("File Name")
    nongmo_required = fields.Boolean("Non GMO Required")
    container_count = fields.Char(compute='_compute_container_count',string="Container")
    products = fields.Char(compute='_compute_products',string="Product")
    igm_no = fields.Char(string="IGM No.")
    igm_date = fields.Date(string="IGM Date")
    igm = fields.Many2one("exim.shipments.igm",string='IGM')
    active = fields.Boolean(string="Active",default=True)
    pending_release_container_count = fields.Char(string='Pending Container',compute="compute_release_count")

    @api.model
    def default_get(self, fields_list):
       res = super(EximShipment, self).default_get(fields_list)
       seq = self.env['exim.shipments.default.sequence'].search([]).default_year.id
       
       res.update({'year': seq})
       _logger.info("Maks" + str(seq))


       return res

    @api.depends('pi_no_id')
    def _compute_consignee(self):
        for rec in self:
            consignee = rec.pi_no_id.consignee_name.id
            rec.consignee_name = consignee


       

    def send_mail_cha(self):
        template_id = self.env.ref('exim.email_to_cha_id').id
        print(template_id , 'template_id.........................................')
        template = self.env['mail.template'].browse(template_id)
        # _logger.info("Templ " + str(template))
        context = self._context
        print(context , 'context.........................................')
        current_uid = context.get('uid')
        print(current_uid , 'current_uid.........................................')
        attach_obj = self.env['ir.attachment'].search([('res_id', '=', self.id )])
        print(attach_obj , 'attach_obj.........................................')
        user = self.env['res.users'].browse(current_uid)
        _logger.info("Templ " + str(user))
        attach_ids=[]
        for i in attach_obj:
            attach_ids.append(i.id)
            # print(i.id)

        # self.message_post_with_template(template_id=template_id.id)

        ctx = {
            'default_model': 'exim.shipments',
            'default_res_id': self.ids[0],
            'default_use_template':True,
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'default_attachment_ids': attach_ids,
            'default_partner_ids': [self.cha.id],
            'default_email_from': user.email,
            'default_subject': str(self.shipment_no) 
        }

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx
        }
    

    def compute_release_count(self):
        for record in self:
            try:
                igm_id = record.igm.id
                if igm_id:
                    count = self.env["igm.containers.detail"].search_count([('igm_id', '=', igm_id),('release','=',False)])
                    record.pending_release_container_count = str(count)+" Containers Pending"
                else:
                    record.pending_release_container_count = "IGM Not Received"
            
            except:
                 record.pending_release_container_count = None
           


    def _compute_coo(self):
        # pi_id = self.pi_no_id
        for record in self:
            record.coo = record.pi_no_id.country_of_origin.country.name
            record.pod = record.pi_no_id.port_of_discharge.port
        # if pi_id:
        #     # try:
        #         # for record in self:
        #         #     _logger.info("saka 1" + str(record.pi_id.country_of_origin.country.name))
        #         #     _logger.info("saka 2" + str(record.pi_id.country_of_origin.country.name))
        #         #     record.coo = record.pi_id.country_of_origin.country.name
        #         #     record.pod = record.pi_id.port_of_discharge.port
        #     # except:
        #     #     pass
        #     pass


    # def _compute_pod(self):
    #     if self.pi_no_id:

    def button_released(self):

        if self.igm.id == False:
             raise ValidationError("IGM is Required")

        else:

            if len(self.igm.container_details) == 0:
                raise ValidationError("Atleast one Container is Required")

            else:
            
                for container in self.igm.container_details:
                    if container.ooc == False:
                        raise ValidationError("OOC in "+str(container.container_no)+" must be Checked")
                    else:        
                        if container.cfs_out_date == False:
                            raise ValidationError("CFS OUT date in Container "+str(container.container_no)+" is required")
                        if container.release == False:
                            raise ValidationError("Container "+str(container.container_no)+" Must be release ")
            
            self.igm.release_visible = True
            
            

                
        

        self.write({'state': 'released' })

    def button_confirm(self):
        
        self.write({'state': 'confirmed' })


    def button_igm_received(self):
        
        _logger.info("Commercial Invoice " + str(self.commercial_invoice.invoice_no ))
        if self.commercial_invoice.invoice_no == False:
            raise ValidationError("Commercial Invoice is Required")

        if self.boe_no == False:
            raise ValidationError("BOE Number is required")
        
        if self.boe_date == False:
            raise ValidationError("BOE DATE is required")

        
        if self.igm_no == False:
            raise ValidationError("IGM Number is required")
        
        if self.igm_date == False:
            raise ValidationError("IGM Date is required")


        self.write({"state":"igm"})

    
    def igm_action(self):
        # self = self.with_context({'default_shipment_id': self.id, 'active_id': self.id}) 

        if self.pi_no_id.product_details[0].grade:
            grade = self.pi_no_id.product_details[0].grade
        else:
            grade = ''

        return {
         'type':'ir.actions.act_window',
         'name':'IGM',
         'res_model':'exim.shipments.igm',
         'domain':[('shipment_no','=',self.id)],
         'view_mode':'tree,form',
         'target':'current',
         'context': { 
                        'default_shipment_no': self.id,
                        'default_lot_no': self.lot_no, 
                        'default_boe_no': self.boe_no, 
                        'default_igm_no': self.igm_no,
                        'default_boe_date': self.boe_date,  
                        'default_igm_date': self.igm_date,
                        'default_grade': grade,
                        'default_invoice_value': self.commercial_invoice.amount_total  
                    }
         }



    def shipments_ci_action(self):
        self = self.with_context({'default_shipment_id': self.id, 'active_id': self.id}) 
        _logger.info("Context "+ str(self._context)) 

        return {
         'type':'ir.actions.act_window',
         'name':'Commercial Invoice',
         'res_model':'exim.shipments.ci',
         'domain':[('shipment_id','=',self.id)],
         'view_mode':'tree,form',
         'target':'current',
         'context': {
                    'default_shipment_id': self.id, 
                    'default_country_of_origin': self.pi_no_id.country_of_origin.id , 
                    'default_port_of_embarkation': self.pi_no_id.port_of_embarkation.id,
                    'default_country_of_destination':  self.pi_no_id.country_of_destination.id ,
                    'default_port_of_discharge' : self.pi_no_id.port_of_discharge.id ,
                    'default_beneficiary_name' : self.pi_no_id.shipper_name.beneficiary_name,
                    'default_bank_name': self.pi_no_id.shipper_name.bank_name,
                    'default_bank_address': self.pi_no_id.shipper_name.bank_address,
                    'default_branch': self.pi_no_id.shipper_name.branch,
                    'default_swift_code': self.pi_no_id.shipper_name.swift_code,
                    'default_iban': self.pi_no_id.shipper_name.iban,
                    'default_payment_terms': self.pi_no_id.payment_terms,
                    'default_lot_no': self.lot_no

                    }
         }

    def _compute_eta_before_five_days(self):
        for shipment in self:
            if shipment.eta:
                date = shipment.eta - timedelta(days=5)
                shipment.eta_before_fivedays = date
                _logger.info("Date - five day" + str(date) )
            if shipment.etd:
                date = shipment.etd + timedelta(days=5)
                shipment.etd_after_fivedays = date


    @api.model
    def create(self, values):
        # prefix = self.pi_no_id.consignee_name.prefix
        pi_id = values["pi_no_id"]
        pi = self.env['exim.pi'].search([("id","=",pi_id)])
        if pi.state == "complete":
            raise ValidationError("PI is Already Closed")
        consignee_id =self.env['exim.pi'].search([("id","=",pi_id)]).consignee_name.id
        consignee_prefix = self.env['exim.pi'].search([("id","=",pi_id)]).consignee_name.prefix
        _logger.info('Consignee Id :' + str(consignee_id))
        seq_id = self.env['exim.shipments.default.sequence'].search([]).default_year.id
        _logger.info('Seq Id :' + str(seq_id))
        seq_year = self.env['exim.shipments.default.sequence'].search([]).default_year.year
        count = self.env['exim.shipments'].search_count([('year','=',seq_id),('consignee_name','=',consignee_id)])
        _logger.info('Values :' + str(values))
        values["shipment_no"] = str(consignee_prefix)+"/"+str(count+1)+"/"+str(seq_year)
       
       
        product_prefixes = ""
        for i in pi.product_details:
            product_prefixes += str("-"+i.product_id.prefix)
        shipper = values["carrier"]
        shipper_prefix = self.env['res.partner'].search([("id","=",shipper)]).prefix
        values["lot_no"] = str(shipper_prefix)+"/"+product_prefixes+"/"+str(count+1)
        new = super().create(values)
        
        return new



    def _compute_products(self):
       for shipment in self:
            if shipment.commercial_invoice:
                product = []
                for product_detail in shipment.commercial_invoice.product_detail:
                    product.append(product_detail.product.name)

                if len(product) > 0:
                    if len(product) == 1:
                        shipment.products = product[0]
                    else:
                        count = len(product) - 1
                        firstproduct = product[0]
                        string = firstproduct +" +"+ str(count)+ " More"
                        shipment.products = string
                else:
                    shipment.products = "No Products"
            else:
                shipment.products = "No Products"

    @api.depends('eta','arriving_in_days')
    def _compute_arriving_time(self):
        for shipment in self:
            fmt = '%Y-%m-%d'
            current_date = datetime.now()
            end_date = shipment.eta
            date_diff = (shipment.eta-current_date).days
            shipment.arriving_in_days = date_diff
            if date_diff >= 0:
                shipment.arriving_in = str(date_diff) + " Days"
            elif shipment.state == 'released':
                shipment.arriving_in = "Arrived"
            else:
                shipment.arriving_in = str(abs(date_diff)) + " Days late"


    def _compute_container_count(self):
        for shipment in self:
            if len(shipment.container_details) > 0:
                if len(shipment.container_details) == 1:
                    firstcontainer = shipment.container_details[0].container_no
                    shipment.container_count = firstcontainer
                else:
                    count = len(shipment.container_details) - 1
                    firstcontainer = shipment.container_details[0].container_no
                    string = firstcontainer +" +"+ str(count)+ " More" 
                    shipment.container_count = string
            else:
                shipment.container_count = "No Containers"



    @api.depends('pi_no_id')
    def _compute_shipper(self):
        for shipment in self:
            if shipment.pi_no_id:
                shipment.shipper_id = shipment.pi_no_id.shipper_name
            else:
                shipment.shipper_id = None


    @api.onchange("cha")
    def set_domain_for_cha(self):
        category = self.env['res.partner.category'].search([('name', '=','CHA' )])
        _logger.info("Working " + str(category))
        partner_id = []
        for i in category.partner_ids:
            _logger.info("Working 2 " + str(i))
            partner_id.append(i.id)
            # _logger.info( "CHA : " + str(i.id))
        result = { 
                    'domain': {'cha': [ 
                    ('id', 'in', partner_id)] 
                    } 
                 } 
        return result
    
    @api.onchange("carrier")
    def set_domain_for_carrier(self):
        category = self.env['res.partner.category'].search([('name', '=','Carrier' )])
        _logger.info("Working " + str(category))
        partner_id = []
        for i in category.partner_ids:
            _logger.info("Working 2 " + str(i))
            partner_id.append(i.id)
            # _logger.info( "CHA : " + str(i.id))
        result = { 
                    'domain': {'carrier': [ 
                    ('id', 'in', partner_id)] 
                    } 
                 } 
        return result
    # country = fields.related('picking_id', 'x_country', type='many2one' ,relation='stock.picking', store=True, string='Country of Origin')


class DefaultShipmentSequence(models.Model):
    _name = 'exim.shipments.default.sequence'
    default_year = fields.Many2one('exim.shipments.sequence',string="Default Year")


class DefaultShipmentSequence(models.Model):
    _name = 'exim.shipments.sequence'
    _rec_name = 'year'
    year = fields.Char("Year")
    

class EximShipmentContainer(models.Model):
    _name = 'exim.shipments.container'
    _rec_name = 'container_no'
    shipment_id =  fields.Many2one('exim.shipments',string="Shipment")
    container_no = fields.Char('Container No')
    container_weight = fields.Integer('Weight')





class EximShipmentCommercialInvoice(models.Model):
    _name = 'exim.shipments.ci'
    _rec_name = 'invoice_no'
    _description = "Commercial Invoice"
    _inherit = ['mail.thread','mail.activity.mixin'] 
    shipment_id = fields.Many2one("exim.shipments" , string="Shipment")
    invoice_no = fields.Char("Invoice No." , required=True)
    port_of_embarkation = fields.Many2one('configuration.port.child',string="Port of Embarkation",required=True,domain="[('parent_field_id', '=', country_of_origin)]")
    country_of_origin = fields.Many2one('configuration.port.parent',string="Country of Origin",required=True)
    port_of_discharge = fields.Many2one('configuration.port.child',string="Port of Discharge",required=True,domain="[('parent_field_id', '=', country_of_destination)]")
    country_of_destination = fields.Many2one('configuration.port.parent',string="Country of Destination",required=True)
    product_detail = fields.One2many('exim.shipment.ci.product','ci_id',string="Product Detail",required=True)
    no_of_packages = fields.Integer("Number of Packages")
    gross_weight = fields.Integer("Gross Weight")
    net_weight = fields.Integer("Net Weight")
    no_of_pallets = fields.Integer("Number of Pallets")
    lot_no = fields.Char("Lot No")
    payment_terms = fields.Text("Payment Terms")
    beneficiary_name = fields.Text("Beneficiary Name")
    bank_name = fields.Text("Bank Name")
    bank_address = fields.Text("Bank Address")
    branch = fields.Char("Branch")
    swift_code = fields.Char("Swift Code")
    iban = fields.Char("IBAN")
    currency_id = fields.Many2one('res.currency',compute='_compute_currency', inverse='_set_uom',string='Currency' ,required=True)
    amount_total = fields.Monetary('Total',compute='_compute_total_amount', currency_field='currency_id', required=True) 

    @api.model
    def default_get(self, fields_list):
       res = super(EximShipmentCommercialInvoice, self).default_get(fields_list)
       vals = []
       _logger.info("Working " + str(res))
       if res:
        shipment = self.env['exim.shipments'].search([('id', '=', res["shipment_id"] )])
        product = shipment.pi_no_id.product_details
        currency = shipment.pi_no_id.currency_id.id
        for i in product:
        #         _logger.info("Prod " + str(i.product_id))
                data = (0, 0, {'product': i.product_id.id, 'currency_id': currency , 'unit_price':i.price , 'quantity_box': 0})
                vals.append(data)

        res.update({'product_detail': vals})
       return res

    @api.model
    def create(self, values):
        CommercialInvoice = self.env['exim.shipments.ci']
        

        # _logger.info("Working" + str(values))
        limit = CommercialInvoice.search_count([('shipment_id','=', values["shipment_id"])])
        # _logger.info("Working" + str(limit))
        if(limit >= 1):
            raise ValidationError("Only One Commercial Invoice Allowed Per Shipment")
        else:
            created = super(EximShipmentCommercialInvoice, self).create(values)
            shipements = self.env['exim.shipments'].search([("id","=",created.shipment_id.id)])
            for record in shipements:
                record.write({  'commercial_invoice': created.id })

        return created

    @api.depends('product_detail')
    def _compute_total_amount(self):
        for ci in self:
            sum = 0
            for product_detail in ci.product_detail:
                sum = sum + product_detail.line_total
            ci.amount_total = sum
    
    def _set_uom(self):
        pass

    @api.depends('shipment_id')
    def _compute_currency(self):
        for ci in self:
            if ci.shipment_id:
                ci.currency_id = ci.shipment_id.pi_no_id.currency_id
            else:
                ci.currency_id = None

    

class ProductCommercialInvoice(models.Model):
    _name = 'exim.shipment.ci.product'
    _rec_name = 'product'
    ci_id = fields.Many2one('exim.shipments.ci',string="CI ID")
    packing_type = fields.Char("Packing Type")
    product = fields.Many2one('product.template',"Product",required=True)
    unit_price = fields.Monetary("Unit Price",currency_field='currency_id',required=True)
    quantity_box = fields.Integer("Net Wt",required=True)
    qt_box = fields.Integer("Qty Box",required=True)
    line_total = fields.Monetary("Line Total",currency_field='currency_id',compute='_calculate_line_total',required=True)
    currency_id = fields.Many2one('res.currency',compute='_compute_currency', inverse='_set_uom',string='Currency' ,required=True)
    # final_amount = fields.Monetary("Final Amount",compute='_compute_final_amount', currency_field='currency_id')


    @api.depends('ci_id')
    def _compute_currency(self):
        for product_detail in self:
            if product_detail.ci_id:
                product_detail.currency_id = product_detail.ci_id.currency_id
            else:
                product_detail.currency_id = None

    def _set_uom(self):
        pass
        
    @api.depends('unit_price','quantity_box')
    def _calculate_line_total(self):
        for x in self:
                x.line_total = x.unit_price * x.quantity_box
        

    
    # @api.depends('line_total')
    # def _compute_final_amount(self):
    #     for pi in self:
    #         sum = 0.0
    #         for product_detail in pi.line_total:
    #             sum = sum + product_detail.line_total
    #         pi.final_amount = sum

            # created = super(EximShipmentCommercialInvoice, self).create(values)
            # shipements = self.env['exim.shipments'].search([("id","=",created.shipment_id.id)])
            # for record in shipements:
            #     record.write({  'commercial_invoice': created.id })
            # return created
    


        
