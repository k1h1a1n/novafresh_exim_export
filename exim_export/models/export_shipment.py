from odoo import models, fields ,api
from odoo.exceptions import ValidationError
import logging
from datetime import datetime, timedelta


_logger = logging.getLogger(__name__)

class ExportShipment(models.Model):
    _name = 'export.exim.shipment'
    _inherit=['mail.thread','mail.activity.mixin']
    _rec_name = "do_no" 
    _description = "Shipment"
    so_id = fields.Many2one('sale.order',string="Sales Order",required=True)
    export_lot = fields.Many2one('export.lot',string="Lot",required=True)
    do_no = fields.Char(string="DO No.")
    responsible_user = fields.Many2one('res.users','Responsible User', default=lambda self: self.env.user)
    do_date = fields.Date(string="DO Date")
    currency_id = fields.Many2one('res.currency',compute='_compute_currency',string='Currency')
    containers = fields.One2many('export.exim.container','shipment_id',string="Containers")
    account_move_id = fields.Many2one('account.move',string="Invoice")
    terminal_name = fields.Char(string="Terminal Name")
    gate_open = fields.Datetime(string="Gate Open")
    gate_closed = fields.Datetime(string="Gate Closed")
    
    actual_gate_open = fields.Datetime(string="Actual Gate Open")
    actual_gate_closed = fields.Datetime(string="Actual Gate Closed")
    
    container_pickup_time = fields.Datetime(string="Container Pickup Time")
    actual_gatein_time = fields.Datetime(string="Actual Gate In Time")


    gate_in_time = fields.Datetime(string="Gate In Time")
    vessel_load_time = fields.Datetime(string="Vessel Load Time")

    
    ship_arrival = fields.Datetime(string="Ship Arrival Date")
    sailing_date = fields.Datetime(string="Sailing Date")

    sailing_date_aftertwodays = fields.Datetime('Saling Date After 2 Days',compute="_compute_sailing_date_aftertwodays",store=True)
    ship_name = fields.Char(string="Ship Name")
    vgm_cutoff = fields.Datetime(string="VGM Cutoff")
    ssr_request = fields.Boolean(string="SSR Request")
    ssr_extended_date = fields.Datetime(string="Extended Date")
    ssr_charges = fields.Float(string="SSR Charges")
    si_cutoff = fields.Datetime(string="SI Cutoff")
    doc_cutoff = fields.Datetime(string="Doc Cutoff")
    sb_no = fields.Char(string="Shipping Bill No.")
    sb_date = fields.Date(string="Shipping Bill Date")
    freight_charge = fields.Monetary(string="Freight Charges")
    cha_charge = fields.Monetary(string="CHA Charges")
    transport_charge = fields.Monetary(string="Transport Charges")
    gross_loaded_weight = fields.Integer(string="Gross Loaded Weight")
    net_loaded_weight = fields.Integer(string="Net Loaded Weight")
    
    #Documents

    invoice_required = fields.Boolean("Invoice Required")
    phyto_required = fields.Boolean("Phyto Required")
    packing_list_required = fields.Boolean("Packing List Required")
    coo_required = fields.Boolean("COO Required")
    bl_required = fields.Boolean("BL Required")
    ebrc_required = fields.Boolean("EBRC Required")
    test_certificate_required = fields.Boolean("Test Certificate Required")
    others = fields.Boolean("Others Dcoument")

    #Shipping
    
    sb_port = fields.Many2one("configuration.port.child",string="Port")

    state = fields.Selection([('draft', 'Draft'),('do_received', 'Shipment'),('container_picked', 'Post Shipment')],default="draft", string='State')


    @api.depends('sailing_date')
    def _compute_sailing_date_aftertwodays(self):
        for shipment in self:
            if shipment.sailing_date:
                date = shipment.sailing_date + timedelta(days=2)
                shipment.sailing_date_aftertwodays = date
            else:
                shipment.sailing_date_aftertwodays = None
              

    

    @api.depends('so_id')
    def _compute_currency(self):
        for shipment in self:
            if shipment.so_id:
                shipment.currency_id = shipment.so_id.currency_id.id
            else:
                shipment.currency_id = None

    @api.onchange("export_lot")
    def set_field(self):
        _logger.info("SAS" +str(len(self.export_lot)))

        if len(self.export_lot)>0:
            self.terminal_name = self.export_lot.terminal_name.port_name
            self.gate_open = self.export_lot.gate_open
            self.gate_closed = self.export_lot.gate_closed
            self.ship_arrival = self.export_lot.ship_arrival
            self.ship_name = self.export_lot.ship_name
            self.vgm_cutoff = self.export_lot.vgm_cutoff
            self.si_cutoff = self.export_lot.si_cutoff
            self.doc_cutoff = self.export_lot.doc_cutoff
            self.do_no = self.export_lot.do_no
            self.do_date = self.export_lot.do_date
            # self.sb_no = self.export_lot.sb_no
            # self.sb_date = self.export_lot.sb_date
            self.sb_port = self.export_lot.ports
            self.actual_gate_open = self.export_lot.actual_gate_open
            self.actual_gate_closed = self.export_lot.actual_gate_closed
            self.container_pickup_time = self.export_lot.container_pickup_time
            self.actual_gatein_time = self.export_lot.actual_gatein_time
            self.gate_in_time = self.export_lot.gate_in_time
            self.vessel_load_time = self.export_lot.vessel_load_time

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
    def create(self, values):
        shipment = self.env['export.exim.shipment']
        _logger.info("tatas"+str(self._context))
        account_move_id = self._context["default_account_move_id"]
        limit = shipment.search_count([('account_move_id','=', account_move_id)])
        if limit >= 1:
             raise ValidationError("Only One Shipment Allowed Per Invoice")
        else:
            created = super(ExportShipment, self).create(values) 
        return created


    def button_container_picked(self):
        self.write({'state': 'container_picked'})
        # for record in self:
        #     if not record.do_no:
        #         raise ValidationError("DO is required")
        #     elif not record.do_date:
        #         raise ValidationError("DO Date is required")
        #     else:
        #         self.write({'state': 'do_received' })


    def button_do_received(self):

        for record in self:
            if not record.do_no:
                raise ValidationError("DO is required")
            elif not record.do_date:
                raise ValidationError("DO Date is required")
            else:
                self.write({'state': 'do_received' })

    def send_mail_shipment_export(self):
        template_id = self.env.ref('exim_export.exportshipmentemail_to_cha_id').id
        print(template_id , 'template_id.........................................')
        attach_obj = self.env['ir.attachment'].search([('res_id', '=', self.id )])
        print(attach_obj , 'attach_obj.........................................')
        context = self._context
        print(context , 'context.........................................')
        current_uid = context.get('uid')
        print(current_uid , 'current_uid.........................................')
        user = self.env['res.users'].browse(current_uid)
        _logger.info("Templ by afzal khan 😂 " + str(user))
        print('came here to check send mail  😂')
        attach_ids=[]
        for i in attach_obj:
            attach_ids.append(i.id)

        ctx = {
            'default_model': 'export.exim.shipment',
            'default_res_id': self.ids[0],
            'default_use_template':True,
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'default_attachment_ids': attach_ids,
            # 'default_partner_ids': 'khan afzal',
            'default_email_from': user.email,
            'default_subject': 'my subject'
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


class ExportContainer(models.Model):
    _name = 'export.exim.container'
    _description = "Container"
    shipment_id = fields.Many2one('export.exim.shipment',string="Shipment")
    container_type = fields.Selection([('dry', 'Dry'),('refer', 'Refer')], string='Container Type')
    container_no = fields.Char(string="Container No.")
    container_weight = fields.Integer(string="Weight")
