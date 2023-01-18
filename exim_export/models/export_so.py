from odoo import models, fields , api
from odoo.exceptions import ValidationError
from lxml import etree
import logging

_logger = logging.getLogger(__name__)


class ExportSalesOrde(models.Model):
    _inherit = 'sale.order'

    shipment_count = fields.Integer(string="Shipment", compute="_compute_shipment_count")
    lot_count = fields.Integer(string="Lots", compute="_compute_lot_count")



    def action_view_lots(self):

        return {
         'type':'ir.actions.act_window',
         'name':'Lots',
         'res_model':'export.lot',
         'domain':[('so_id','=',self.id)],
         'view_mode':'tree,form',
         'target':'current',
         'context': { 
                       'default_so_id':self.id 
                    }
         }
    
    def action_view_costing(self):
        
        
        return {
         'type':'ir.actions.act_window',
         'name':'Costing',
         'res_model':'sale.order.costing',
         'domain':[('so_id','=',self.id)],
         'view_mode':'tree,form',
         'target':'current',
         'context': { 
                       'default_so_id':self.id 
                    }
         }


    def _compute_lot_count(self):
        lot = self.env['export.lot']
        for so in self:
            so.lot_count = lot.search_count([('so_id','=',so.id)])


    def _compute_shipment_count(self):
        Shipment = self.env['export.exim.shipment']
        for so in self:
            so.shipment_count = Shipment.search_count([('so_id','=',so.id)])
    

    def action_view_shipment(self):



        return {
         'type':'ir.actions.act_window',
         'name':'Shipment',
         'res_model':'export.exim.shipment',
         'domain':[('so_id','=',self.id)],
         'view_mode':'tree,form',
         'target':'current',
         'context': { 
                       'default_so_id':self.id 
                    }
         }


        #  return {
        #     'name': _('Customer Invoice'),
        #     'view_mode': 'form',
        #     'view_id': self.env.ref('account.view_move_form').id,
        #     'res_model': 'account.move',
        #     'context': "{'move_type':'out_invoice'}",
        #     'type': 'ir.actions.act_window'
        # }

        # return {
        #     'name': _('Customer Invoice'),
        #     'view_mode': 'form',
        #     'view_id': self.env.ref('account.view_move_form').id,
        #     'res_model': 'account.move',
        #     'context': "{'move_type':'out_invoice'}",
        #     'type': 'ir.actions.act_window',
        #     'res_id': self.account_move.id,
        # }


# class ExportInvoice(models.Model):
#     _inherit = 'account.move'
#     export_shipment_id = fields.Many2one('export.exim.shipment',string='Shipment ID')



class ExportSalesOrderLine(models.Model):
    _inherit = 'sale.order.line'
    gross_wt = fields.Float("Gross Weight")
    packing = fields.Float("Packing")


class ExportInvoice(models.Model):
    _inherit = 'account.move.line'
    gross_wt = fields.Float("Gross Weight")
    packing = fields.Float("Packing")




class ExportAccountMove(models.Model):
    _inherit = 'account.move'
    export_lot = fields.Many2one('export.lot',string="Lot")

    # def fields_view_get(self, view_id=None, view_type='Form', toolbar=False, submenu=None):
    #     # if context is None:
    #     #     context = {}
    #     result = super().fields_view_get( view_id=view_id, view_type=view_type,  toolbar=toolbar, submenu=submenu)
       
    #     so_id = self._context.get("active_id")
 
    #     lot_ids=[]
    #     lot = self.env['export.lot']
    #     lots = lot.search([('so_id','=', so_id)])
    #     for lot in lots:
    #         lot_ids.append(lot.id)

    #     lot_ids = tuple(lot_ids)

    #     _logger.info("From Field View Lots ids" + str(lot_ids))
    #     if view_type == 'form':
    #         # _logger.info("From Field View")
    #         doc = etree.XML(result['arch'])
    #         _logger.info("If statement Field View")
    #         nodes = doc.xpath("//field[@name='export_lot']")
    #         _logger.info("Nodes" + str(nodes))
    #         for node in nodes:
    #             _logger.info(str(node))
    #             node.set('domain', "[('id', 'in', "+ str(lot_ids)+" )]")
            
    #         result['arch'] = etree.tostring(doc)
       
    #     return result
        


    # @api.onchange("export_lot")
    # def set_domain_for_lot(self):
        
    #     so_id = self._context.get("active_id")
    #     _logger.info(str(so_id))
    #     # so = self.env['sale.order'].search([('invoice_ids','in', [so_id])])
    #     # context = self._context
    #     # _logger.info("Context " +str(context))
    #     # lot_ids=[]
    #     # lot = self.env['export.lot']
    #     # lots = lot.search([('so_id','=', so.id)])
    #     # for lot in lots:
    #     #     lot_ids.append(lot.id)
    #     result = { 
    #                 'domain': {'export_lot': [ 
    #                 ('id', 'in', [1])] 
    #                 } 
    #              } 
    #     return result
    
    # @api.onchange("partner_id")
    # def set_domain_for_lot(self):
        
    #     so_id = self._context.get("active_id")
    #     _logger.info(str(so_id))
    #     # so = self.env['sale.order'].search([('invoice_ids','in', [so_id])])
    #     # context = self._context
    #     # _logger.info("Context " +str(context))
    #     # lot_ids=[]
    #     # lot = self.env['export.lot']
    #     # lots = lot.search([('so_id','=', so.id)])
    #     # for lot in lots:
    #     #     lot_ids.append(lot.id)
    #     result = { 
    #                 'domain': {'export_lot': [ 
    #                 ('id', 'in', [1])] 
    #                 } 
    #              } 
    #     return result


    def action_view_shipment(self):
            # context = self._context
            # _logger.info("Context " +str(context))


            so = self.env['sale.order'].search([('invoice_ids','in', [self.id])])

            

            return {
            'type':'ir.actions.act_window',
            'name':'Shipment',
            'res_model':'export.exim.shipment',
            'domain':[('account_move_id','=',self.id)],
            'view_mode':'tree,form',
            'target':'current',
            'context': { 
                        'default_account_move_id':self.id,
                        'default_so_id':so.id,
                        'default_sb_no':self.l10n_in_shipping_bill_number,
                        'default_sb_date':self.l10n_in_shipping_bill_date
                        }
            }

    

    def action_view_dbk(self):
        
        so = self.env['sale.order'].search([('invoice_ids','in', [self.id])])

        partner = self.partner_id.id

        # _logger.info(self.partner_id.id)

        return {
            'type':'ir.actions.act_window',
            'name':'DBK',
            'res_model':'export.invoice.dbk',
            'domain':[('account_move_id','=',self.id)],
            'view_mode':'tree,form',
            'target':'current',
            'context': { 
                        'default_account_move_id':self.id,
                        'default_so_id':so.id,
                        'default_consignee':partner,
                        'default_sb_no':self.l10n_in_shipping_bill_number,
                        'default_sb_date':self.l10n_in_shipping_bill_date
                        }
            }

class SoBill(models.Model):
    _name = "sale.order.costing"
    _inherit=['mail.thread','mail.activity.mixin']
    _rec_name = 'so_id'

    # Transport Costing
    so_id = fields.Many2one('sale.order',string="Sales Order",required=True)
    transports = fields.One2many('sale.order.costing.transport','so_costing_id',string="Transport")
    total_transporting_cost  = fields.Integer(string="Total Transporting Cost" , compute="_compute_total_transporting_cost")

    total_shipping_cost = fields.Integer("Total Shipping Cost", compute="_compute_total_shipping_cost")

    # Shipping
    shipping_line_cost = fields.Integer(string="Shipping Line Cost")
    shipping_line = fields.Many2one('res.partner',string="Shipping Line")
    freight = fields.Integer(string="Freight")
    bill_no = fields.Char(string="Bill No.")
    shipping_line_paid = fields.Boolean("Paid")

    #CHA

    cha = fields.Many2one('res.partner',string="CHA")
    cha_cost = fields.Integer(string="CHA Cost")
    cha_bill_no = fields.Char(string="Bill No.")
    cha_paid = fields.Boolean("Paid")

    #Inspection Agency
    inspection_agency = fields.Many2one('res.partner',string="Inspection Agency")
    inspection_cost = fields.Integer(string="Inspection Cost")
    inspection_bill_no = fields.Char(string="Bill No.")

    #Test Report
    test_report = fields.Many2one('res.partner',string="Test Report Contact")
    test_cost = fields.Integer(string="Inspection Cost")
    test_bill_no = fields.Char(string="Bill No.")
    test_paid = fields.Boolean("Paid")

    per_kg_cost = fields.Float("Per KG Cost",compute="_compute_per_kg_cost")

    per_pack_cost = fields.Float("Per Pack Cost",compute="_compute_per_pack_cost")



    @api.depends('transports.account_move_id','shipping_line_cost','cha_cost','inspection_cost','test_bill_no')
    def _compute_per_pack_cost(self):
        try:
            packing = 0
            for i in self.transports.account_move_id.invoice_line_ids:
                packing = packing + i.packing
            
            _logger.info("Packing " + str(packing))
            for rec in self:
                rec.per_pack_cost = rec.total_shipping_cost / packing
        except:
            rec.per_pack_cost = 0
           

        
        #  try:
        #         record.per_kg_cost = 0
        #         container_weight = 0
        #         for container in record.transports:
        #             container_weight = container_weight + container.weight
            
        #         record.per_kg_cost = record.total_shipping_cost / container_weight
        # except:
        #         record.per_kg_cost = 0

   
    def write(self, values):
        _logger.info("Values "+ str(values['transports']))
        for i in values['transports']:
            _logger.info("sas "+str(i))
        for transport in values["transports"]:
            if transport[2]:
                transport_id = transport[1]
                bill_no = transport[2]['bill_no']
                container_no = self.env['sale.order.costing.transport'].search([('id','=', transport_id)]).container
                transport = self.env['sale.order.costing.transport'].search([('container','=', container_no),('bill_no','=',bill_no)])
                if len(transport) >= 1:
                    raise ValidationError(str(container_no)+" With Bill No. " +str(bill_no)+" already Exist")
        # for transport in self.transports:
        #     _logger.info("sas "+str(transport.container))
        #     # if not bill_no:
        #     #     raise ValidationError(str(container)+" Required Bill No.")
        #     transport = self.env['sale.order.costing.transport'].search([('container','=', container),('bill_no','=', bill_no)])
        #     _logger.info("sas "+str(len(transport)))
            
            # if len(transport) >= 1:
            #     raise ValidationError(str(container)+" With Bill No. " +str(bill_no)+" already Exist")
            

        new = super(SoBill, self).write(values)
        return new

    @api.model
    def create(self, values):


        costing = self.env['sale.order.costing']
        limit = costing.search_count([('so_id','=', values["so_id"])])
        if limit >= 1:
             raise ValidationError("Only One Costing Allowed Per Sales Order")
       
       
        for transport in values["transports"]:
            
            container = transport[2]['container']
            bill_no = transport[2]['bill_no']
            # if not bill_no:
            #     raise ValidationError(str(container)+" Required Bill No.")
            transport = self.env['sale.order.costing.transport'].search([('container','=', container),('bill_no','=', bill_no)])
            _logger.info("sas "+str(len(transport)))
            
            if len(transport) >= 1:
                raise ValidationError(str(container)+" With Bill No. " +str(bill_no)+" already Exist")
            
            # shipping_bill_no = values["bill_no"]
            # _logger.info("sasa"+ str(shipping_bill_no))
            # if shipping_bill_no:
            #     bill_no = self.env['sale.order.costing'].search([('bill_no','=',shipping_bill_no)])
            #     if len(bill_no) >= 1:
            #         raise ValidationError("Shipping Bill No. Already Exist")
            # else:
            #     raise ValidationError("Shipping Bill No. Required")
            
            # cha_bill_no = values["cha_bill_no"]
            # if cha_bill_no:
            #     cha_bill_no = self.env['sale.order.costing'].search([('cha_bill_no','=',cha_bill_no)])
            #     if len(cha_bill_no) >= 1:
            #         raise ValidationError("CHA Bill No. Already Exist")
            # else:
            #     raise ValidationError("CHA Bill No. Required")
            

            # inspection_bill_no = values["inspection_bill_no"]
            # if inspection_bill_no:
            #     inspection_bill_no = self.env['sale.order.costing'].search([('inspection_bill_no','=',inspection_bill_no)])
            #     if len(inspection_bill_no) >= 1:
            #         raise ValidationError("Inspection Bill No. Already Exist")
            # else:
            #     raise ValidationError("Inspection Bill No. Required")
            

            # test_bill_no = values["test_bill_no"]
            # if test_bill_no:
            #     test_bill_no = self.env['sale.order.costing'].search([('inspection_bill_no','=',test_bill_no)])
            #     if len(test_bill_no) >= 1:
            #         raise ValidationError("Test Bill No. Already Exist")
            # else:
            #     raise ValidationError("Test Bill No. Required")



            
        new = super().create(values)
        return new


    @api.depends('total_shipping_cost')
    def _compute_per_kg_cost(self):
        for record in self:
            try:
                record.per_kg_cost = 0
                container_weight = 0
                for container in record.transports:
                    container_weight = container_weight + container.weight
            
                record.per_kg_cost = record.total_shipping_cost / container_weight
            except:
                record.per_kg_cost = 0


    @api.depends('total_transporting_cost','freight','cha_cost','inspection_cost','test_cost')
    def _compute_total_shipping_cost(self):
        for record in self:
            try:
                record.total_shipping_cost = record.total_transporting_cost + record.freight + record.cha_cost + record.inspection_cost + record.test_cost
            except:
                record.total_shipping_cost = None


    @api.depends('transports.transporter_charges','total_transporting_cost')
    def _compute_total_transporting_cost(self):
        try:
            for record in self:
                record.total_transporting_cost = 0
                sum = 0
                for charges in record.transports:
                    sum = sum + charges.transporter_charges
                    record.total_transporting_cost = sum
        except:
            record.total_transporting_cost = 0
            




    @api.model
    def default_get(self, fields_list):
       res = super(SoBill, self).default_get(fields_list)
       transports = []
       try:
        
        if res:
            so_id = res["so_id"]
            
            shipments = self.env['export.exim.shipment'].search([('so_id','=', so_id)])
            for shipment in shipments:
                invoices = shipment.account_move_id 
                _logger.info("SAKA"+str(invoices))
                for invoice in invoices:
                    
                    shipment = self.env['export.exim.shipment'].search([('account_move_id','=', invoice.id)])
                    containers = shipment.containers
                    invoice_id = invoice.id

           
                    _logger.info(containers)
                    for i in containers:
                        
                        # _logger.info(i.weight)
                        data = (0, 0, {'account_move_id':invoice_id,'container':i.container_no,'container_pickup_time':shipment.container_pickup_time,'actual_gatein_time':shipment.actual_gatein_time,'gate_in_time':shipment.gate_in_time,'vessel_load_time':shipment.vessel_load_time, 'weight':i.container_weight})
                        _logger.info(data)
                        transports.append(data)        
                #     # for container in shipment.containers:
                #     #     _logger.info("sakaa"+str(container))
                #     #     transports.append(data)
                # _logger.info("kaka"+str(transports))

            res.update({'transports':transports})
       except:
        res.update({})
       return res









class SoBillTransport(models.Model):
    _name = "sale.order.costing.transport"
    so_costing_id = fields.Many2one('sale.order.costing',string="Sales Order",required=True)
    account_move_id = fields.Many2one('account.move',string="Invoice")
    container = fields.Char(string="Container No.")
    weight = fields.Integer(string="Weight.")
    container_pickup_time = fields.Datetime(string="Container Pickup Time")
    actual_gatein_time = fields.Datetime(string="Actual Gate In Time")
    
    container_pickup_time_diff = fields.Char(string="Time Difference",compute="_compute_container_pickup_time_diff")

    gate_in_time = fields.Datetime(string="Gate In Time")
    vessel_load_time = fields.Datetime(string="Vessel Load  Time")
    
    vessel_time_diff = fields.Char(string="Time Difference",compute="_compute_vessel_time_diff")

    transporter_name = fields.Many2one('res.partner',string="Transporter Name")
    transporter_charges = fields.Integer(string="Transporter Charges")
    bill_no = fields.Char(string="Bill No.")
    vehicle_no = fields.Char(string="Vehicle No.")
    paid = fields.Boolean("Paid")

    @api.depends('bill_no')
    def check_duplicate_bills(self):
        for rec in self:

            shipments = self.env['sale.order.costing.transport'].search([('container','=', rec.container),('bill_no','=',rec.bill_no)])
            _logger.info("asasa"+str(shipments))


    @api.depends('container_pickup_time','actual_gatein_time')
    def _compute_container_pickup_time_diff(self):
        for rec in self:
            try:
                start_time = rec.container_pickup_time
                end_time = rec.actual_gatein_time
                delta = end_time - start_time
                rec.container_pickup_time_diff = delta
            except:
                rec.container_pickup_time_diff = None
    
    @api.depends('gate_in_time','vessel_load_time')
    def _compute_vessel_time_diff(self):
        for rec in self:
            try:
                start_time = rec.gate_in_time
                end_time = rec.vessel_load_time
                delta = end_time - start_time
                rec.vessel_time_diff = delta
            except:
                rec.vessel_time_diff = None
