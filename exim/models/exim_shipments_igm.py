from dataclasses import field
from datetime import datetime, timedelta
from email.base64mime import body_encode
from locale import currency
from this import d
from odoo import models, fields , api
from odoo.exceptions import ValidationError
from datetime import datetime,timedelta


import logging

_logger = logging.getLogger(__name__)

class EximShipmentIGM(models.Model):
    _name = 'exim.shipments.igm'
    _description = "IGM"
    _rec_name = 'shipment_no'
    _inherit = ['mail.thread','mail.activity.mixin'] 
    shipment_no = fields.Many2one("exim.shipments",string='Shipment')
    foreign_currency = fields.Many2one('res.currency', string="Foreign Currency")
    home_currency = fields.Many2one('res.currency', string="Home Currency")
    lot_no = fields.Char(string='Lot no.')
    grade = fields.Char(string='Grade.')
    container_no = fields.Char(string='Container No.')
    boe_no = fields.Char(string='BOE No.')
    boe_date = fields.Date(string='BOE Date')
    igm_no = fields.Char(string='IGM No.')
    igm_date = fields.Date(string='IGM Date')
    inward_date = fields.Date(string='Inward Date')
    invoice_value = fields.Monetary('Invoice Value' , currency_field ='foreign_currency')
    ex_rate = fields.Monetary("Exchange Rate", currency_field ='home_currency')
    invoice_value_inr = fields.Monetary('Invoice Value(INR)',compute="_compute_rate_inr", currency_field ='home_currency')
    insurance = fields.Monetary("Insurance" , currency_field ='home_currency')
    freight = fields.Monetary("Freight" , currency_field ='foreign_currency')
    freight_inr = fields.Monetary("Freight INR",compute="_compute_rate_inr", currency_field ='home_currency')
    cif_value = fields.Monetary("CIF VALUE",compute="_compute_cif_value", currency_field ='home_currency')
    duty_bcd = fields.Monetary("Duty (BCD)" , currency_field ='home_currency')
    duty_sws = fields.Monetary("Duty (SWS)" , currency_field ='home_currency')
    duty_aidc = fields.Monetary("Duty (AIDC)" , currency_field ='home_currency')
    duty_gst = fields.Monetary("Duty (GST)" , currency_field ='home_currency')
    shipping_line = fields.Monetary("Shipping Line" , currency_field ='home_currency')
    cfs = fields.Monetary("CFS" , currency_field ='home_currency')
    ci_product_line_item = fields.Many2one("exim.shipment.ci.product",string="CI Line Item")
    fssai = fields.Monetary("FSSAI" , currency_field ='home_currency')
    pq = fields.Monetary("PQ" , currency_field ='home_currency')
    container_details = fields.One2many('igm.containers.detail','igm_id',string="Container Detail",required=True)
    cha = fields.Monetary("CHA" , currency_field ='home_currency')
    others = fields.Monetary("Others" , currency_field ='home_currency')
    landing_cost = fields.Monetary("Landing Cost",compute="_compute_landing_cost" , currency_field ='home_currency')
    per_box_cost = fields.Monetary("Per KG Cost" , compute="_compute_pb_cost" ,currency_field ='home_currency')
    box_qty = fields.Integer(string="Box Qty" , compute="_compute_box_qty")
    ooc =  fields.Boolean(string="OOC")
    port_in_date = fields.Datetime(string="Port IN")
    port_out_date = fields.Datetime(string="Port Out")
    cfs_in_date = fields.Datetime(string="CFS IN")
    cfs_out_date = fields.Datetime(string="CFS OUT")
    duty_details = fields.One2many('igm.duty.line','igm_id',string="Duty Detail",required=True)
    release_visible = fields.Boolean("Release")
    claim_amount = fields.Char(string='Claim Amount')
    claim_settlement_amount = fields.Char(string='Claim Settlement Amount')
    claim_settled = fields.Boolean(string="Claim Settled")
    mapping_status = fields.Char(string='Mapping Status')
    credit_note = fields.Char(string='Credit Note')
    warehouse = fields.Char(string="Warehouse")
    final_noc = fields.Boolean(string="Final Noc")
    quality = fields.Selection([('good', 'Good'),('bad', 'Bad')],string='Quality')
    incoterms =  fields.Selection([('cif', 'CIF'),('fob', 'FOB'),('cnf', 'CNF')], string='Incoterms')
    pb_cost =   fields.Monetary("Per Box Cost" , compute="_compute_pbox_cost" ,currency_field ='home_currency')
    sum_net_wt = fields.Float("Total Net Wt.",compute="_compute_total_netwt")
    cif_details = fields.One2many('igm.cif.line','igm_id',string="CIF Line",required=True)
    actual_weight = fields.Float("Actual Weight")
    sample_weight = fields.Float("Sample Weight")
    unloading_weight = fields.Float("Unloading Weight")
    weight_diff = fields.Float("Weight Diff",compute="_compute_weight_diff")
    br = fields.Char("BR")

    @api.depends("actual_weight","sample_weight","unloading_weight")
    def _compute_weight_diff(self):
        for rec in self:
            try:
                rec.weight_diff = rec.actual_weight - rec.sample_weight - rec.unloading_weight
            except:
                pass
            
    @api.depends("cif_details.qty")
    def _compute_total_netwt(self):
        for rec in self:
            net_wt = 0.0

            for i in rec.cif_details:
                net_wt += i.qty 
            
            rec.sum_net_wt = net_wt
            


    @api.model
    def create(self, values):
        igm = self.env['exim.shipments.igm']
        limit = igm.search_count([('shipment_no','=', values["shipment_no"])])
        if limit >= 1:
             raise ValidationError("Only One IGM Allowed Per Shipment")
        else:
            incoterms = self.env['exim.shipments'].search([("id","=",values["shipment_no"])]).pi_no_id.incoterms
            values["incoterms"] = incoterms
            created = super(EximShipmentIGM, self).create(values)
            shipements = self.env['exim.shipments'].search([("id","=",created.shipment_no.id)])
            
            for record in shipements:
                record.write({  'igm': created.id })
        return created

    @api.depends("landing_cost","cif_details.qty_box")
    def _compute_pbox_cost(self):
        for rec in self:
            total_box = 0.0

            for i in rec.cif_details:
                total_box += i.qty_box
            
            rec.pb_cost =  rec.landing_cost /total_box
            



    @api.depends("landing_cost","cif_details.qty")
    def _compute_pb_cost(self):

         for rec in self:
            total_box = 0.0

            for i in rec.cif_details:
                total_box += i.qty 
            
            rec.per_box_cost =  rec.landing_cost /total_box
            
           


        


        # try:
        #     self.per_box_cost = self.landing_cost / self.box_qty
        # except:
        #     self.per_box_cost = None

    @api.depends("ci_product_line_item","cif_details.invoice_value")
    def _compute_cif_value(self):
        cif = 0.0
        for value in self.cif_details:
            cif += value.cif
        self.cif_value = cif

    @api.depends("ci_product_line_item")
    def _compute_box_qty(self):
        self.box_qty = self.ci_product_line_item.quantity_box

    @api.onchange("shipment_no")
    def set_domain_for_ci_product_line_item(self):

        id = self.shipment_no.commercial_invoice.id
        _logger.info("Sasa "+ str(id))
        result = { 
                    'domain': {'ci_product_line_item': [ 
                    ('ci_id', '=', id)] 
                    } 
                 } 
        return result

    @api.depends('ex_rate','invoice_value','freight')
    def _compute_rate_inr(self):
        # _logger.info("ex_rate " + str(self.ex_rate) + " inv_val "+ str(self.invoice_value) )
        self.invoice_value_inr = self.ex_rate * self.invoice_value
        self.freight_inr = self.ex_rate * self.freight
    
    @api.depends('duty_bcd','duty_sws','shipping_line','cfs','fssai','pq','cha','cif_value')
    def _compute_duty(self):
        self.landing_cost =  self.duty_bcd + self.duty_sws + self.shipping_line + self.cfs + self.fssai + self.pq + self.cha + self.cif_value
    
    @api.depends('cif_details.cif','duty_details.total')
    def _compute_landing_cost(self):

        for rec in self:
            cif_total = 0.0
            for i in rec.cif_details:
                cif_total += i.cif
            
            duty_total = 0.0
            for i in rec.duty_details:
                duty_total += i.total
            rec.landing_cost =  cif_total + duty_total


    @api.model
    def default_get(self, fields_list):
       res = super(EximShipmentIGM, self).default_get(fields_list)
       container_details_vals = []
       cif_details_vals = []
       duty_vals = []
       try:
        if res:
            shipment_no = int(res["shipment_no"])
            _logger.info(str(shipment_no))
            shipment = self.env['exim.shipments'].search([('id', '=', shipment_no )])
            usd_currency = self.env['res.currency'].search([('name', '=', 'USD' )]).id
            inr_currency = self.env['res.currency'].search([('name', '=', 'INR' )]).id
            currency = shipment.pi_no_id.currency_id.id
            ci_id = shipment.commercial_invoice.id
            res["domain"] = {
                            'ci_product_line_item': [ ('ci_id', '=', ci_id)] 
                            }
                
            
            incoterms = shipment.pi_no_id.incoterms

            for container in shipment.container_details:
                data = (0, 0, {'container_no': container.container_no, 'container_weight': container.container_weight })
                container_details_vals.append(data)
            
            for product in shipment.commercial_invoice.product_detail:

                data = (0, 0, { 'ci_product_line_item':product,'qty_box':product.qt_box,'qty':product.quantity_box,'foreign_currency': usd_currency, 'home_currency': inr_currency ,"invoice_value":product.line_total })
                cif_details_vals.append(data)

            for duty in shipment.commercial_invoice.product_detail:
                data = (0, 0, { 'ci_product_line_item':duty})
                duty_vals.append(data)


            if shipment.state == "released":
                
                res.update({'foreign_currency': usd_currency ,'home_currency':inr_currency, 'container_details':container_details_vals,'cif_details':cif_details_vals,'duty_details':duty_vals ,'release_visible': True, 'incoterms':incoterms })

            else:

                res.update({'foreign_currency': usd_currency ,'home_currency':inr_currency, 'container_details':container_details_vals,'cif_details':cif_details_vals,'duty_details':duty_vals,'incoterms':incoterms })
       except:
            res.update({})
       return res

class ContainerDetails(models.Model):
    _name = "igm.containers.detail"
    _inherit = 'exim.shipments.container'
    igm_id =  fields.Many2one('exim.shipments.igm',string="IGM")
    ooc =  fields.Boolean(string="OOC")
    port_in_date = fields.Datetime(string="Port IN")
    port_out_date = fields.Datetime(string="Port Out")
    port_time_diff = fields.Char(string="Port time Diff(HR)",compute="_compute_time_diff")
    cfs_in_date = fields.Datetime(string="CFS IN")
    cfs_out_date = fields.Datetime(string="CFS OUT")
    cfs_time_diff = fields.Char(string="CFS time Diff(HR)",compute="_compute_cfstime_diff")
    transporter_name = fields.Char(string="Transporter Name")
    vehicle_no = fields.Char(string="Vehicle No")
    release =  fields.Boolean(string="Release")


    

    @api.depends('cfs_in_date','cfs_out_date')
    def _compute_cfstime_diff(self):
        for rec in self:
            try:
                start_time = rec.cfs_in_date
                end_time = rec.cfs_out_date
                delta = end_time - start_time
                rec.cfs_time_diff = delta
            except:
                rec.cfs_time_diff = None

    @api.depends('port_in_date','port_out_date')
    def _compute_time_diff(self):
        for rec in self:

            try:
                start_time = rec.port_in_date
                end_time = rec.port_out_date
                _logger.info("start time "  + str(start_time)+ " End time " +str(end_time))
                delta = end_time - start_time
                _logger.info("Delta " + str(delta))
                rec.port_time_diff = delta
            except:
                rec.port_time_diff = None
                
                # sec = delta.total_seconds()
                # hours = sec / (60 * 60)
                # rec.port_time_diff = hours

    

class DutyLine(models.Model):
    _name = "igm.duty.line"
    igm_id =  fields.Many2one('exim.shipments.igm',string="IGM")
    ci_product_line_item = fields.Many2one("exim.shipment.ci.product",string="CI Line Item")
    duty_bcd = fields.Float("BCD",compute="_compute_duty")
    duty_sws = fields.Float("SWS",compute="_compute_duty")
    duty_aidc = fields.Float("AIDC",compute="_compute_duty")
    duty_gst = fields.Float("IGST",compute="_compute_duty")
    penalty = fields.Float("Penalty")
    others = fields.Float("Others")
    shipping_line = fields.Float("Shipping Line" )
    cfs = fields.Float("CFS" )
    fssai = fields.Float("FSSAI")
    pq = fields.Float("PQ")
    cha = fields.Float("CHA")
    transportation_cost = fields.Float("Transportation Cost")
    total = fields.Float("Total",compute="_compute_total")

    @api.onchange("igm_id","ci_product_line_item")
    def set_domain_for_ci_product_line_item(self):
        id = self.igm_id.shipment_no.commercial_invoice.id
      
        
        _logger.info("Sasa ")
        result = { 
                    'domain': {'ci_product_line_item': [ 
                    ('ci_id', '=', id)] 
                    } 
                 } 
        return result

    
    # def _compute_inverse(self):
    #     for rec in self:
    #         if rec.duty_bcd:
    #             rec.duty_bcd = rec.duty_bcd
    #         else:
    #            rec.duty_bcd = rec.igm_id.cif_value * (rec.ci_product_line_item.product.duty_bcd_percentage)

    #         # pass

    @api.depends('igm_id.cif_value','duty_bcd')
    def _compute_duty(self):
        for rec in self:
            rec.ci_product_line_item.id 
            cif_line = self.env['igm.cif.line'].search([('ci_product_line_item', '=', rec.ci_product_line_item.id ),('igm_id','=',rec.igm_id.id)])
            _logger.info(" Line "+str(cif_line))
            rec.duty_bcd = cif_line.cif * (rec.ci_product_line_item.product.duty_bcd_percentage)
            rec.duty_sws = rec.duty_bcd * (rec.ci_product_line_item.product.duty_sws_percentage)
            rec.duty_aidc = cif_line.cif * (rec.ci_product_line_item.product.duty_aidc_percentage)
            rec.duty_gst = (cif_line.cif + rec.duty_bcd + rec.duty_sws) * (rec.ci_product_line_item.product.duty_gst_percentage)




    @api.depends('duty_bcd','duty_sws','duty_aidc','duty_gst','penalty','others','shipping_line','cfs','fssai','pq','cha','transportation_cost')
    def _compute_total(self):
        for rec in self:
            rec.total = rec.duty_bcd + rec.duty_sws + rec.duty_aidc + rec.duty_gst + rec.penalty + rec.others + rec.shipping_line + rec.cfs + rec.fssai + rec.pq + rec.cha + rec.transportation_cost


class CIFLineDetail(models.Model):
    _name = "igm.cif.line"
    incoterms =  fields.Selection([('cif', 'CIF'),('fob', 'FOB'),('cnf', 'CNF')],compute="_compute_incoterm", string='Incoterms')
    igm_id =  fields.Many2one('exim.shipments.igm',string="IGM")
    ci_product_line_item = fields.Many2one("exim.shipment.ci.product",string="CI Line Item")
    qty = fields.Integer(string=" Net Wt" )
    foreign_currency = fields.Many2one('res.currency', string="Foreign Currency")
    home_currency = fields.Many2one('res.currency', string="Home Currency")
    insurance = fields.Monetary("Insurance" , currency_field ='home_currency')
    freight = fields.Monetary("Freight" , currency_field ='foreign_currency')
    freight_inr = fields.Monetary("Freight INR",compute="_compute_rate_inr", currency_field ='home_currency')
    invoice_value = fields.Monetary("Invoice Value" , currency_field ='foreign_currency')
    qty_box = fields.Float("Qty Box")
    invoice_value_inr = fields.Monetary("Invoice Value (INR)",compute="_compute_rate_inr" , currency_field ='home_currency')
    cif = fields.Monetary("CIF" ,compute="_compute_cif", currency_field ='home_currency')



    

    @api.depends('igm_id')
    def _compute_incoterm(self):
        for rec in self:
            # _logger.info("ex_rate" + str(rec) )
            rec.incoterms = rec.igm_id.incoterms
            


    @api.depends('invoice_value','freight','igm_id.ex_rate')
    def _compute_rate_inr(self):
        for rec in self:
            # _logger.info("ex_rate" + str(rec) )
            rec.invoice_value_inr = rec.invoice_value * rec.igm_id.ex_rate
            rec.freight_inr = rec.freight * rec.igm_id.ex_rate
    
    @api.depends('invoice_value_inr','insurance')
    def _compute_cif(self):
        for rec in self:
            # _logger.info("ex_rate" + str(rec) )
            rec.cif = rec.invoice_value_inr + rec.insurance + rec.freight_inr
            # rec.freight_inr = rec.freight * rec.igm_id.ex_rate
    

    # foreign_currency = fields.Many2one('res.currency', string="Foreign Currency")
    # home_currency = fields.Many2one('res.currency', string="Home Currency")



    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(CIFLineDetail, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,submenu=submenu)
        
    #     _logger.info("From CIF Detail ")
    #     result = { 
    #                 'domain': {'ci_product_line_item': [ 
    #                 ('ci_id', '=', 7)] 
    #                 } 
    #              } 
        
        # return result
    
    # @api.model
    # def default_get(self, fields_list):
    #    res = super(CIFLineDetail, self).default_get(fields_list)
    #    usd_currency = self.env['res.currency'].search([('name', '=', 'USD' )]).id
    #    inr_currency = self.env['res.currency'].search([('name', '=', 'INR' )]).id
    #    res.update({'foreign_currency': usd_currency ,'home_currency':inr_currency})
    #    return res

    
    

    @api.onchange("igm_id","ci_product_line_item")
    def set_domain_for_ci_product_line_item(self):
        id = self.igm_id.shipment_no.commercial_invoice.id
      
        
        _logger.info("Sasa ")
        result = { 
                    'domain': {'ci_product_line_item': [ 
                    ('ci_id', '=', id)] 
                    } 
                 } 
        return result

    
