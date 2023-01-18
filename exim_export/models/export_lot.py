from odoo import models, fields ,api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ExportLot(models.Model):
    _name = 'export.lot'
    _rec_name = 'lot_no'
    _description = "Lot"
    _inherit=['mail.thread','mail.activity.mixin']
    lot_no = fields.Char(string="Lot No.",required=True)
    do_no = fields.Char(string="DO No.")
    do_date = fields.Date(string="DO Date")
    so_id = fields.Many2one('sale.order',string="Sales Order",required=True)
    ports = fields.Many2one("configuration.port.child",string="Port")
    port_of_discharge = fields.Many2one("configuration.port.child",string="Port of Discharge")
    terminal_name = fields.Many2one("configuration.terminal.child",string="Terminal")
    gate_open = fields.Datetime(string="Gate Open")
    gate_closed = fields.Datetime(string="Gate Closed")
    ship_arrival = fields.Datetime(string="Ship Arrival Date")
    ship_name = fields.Char(string="Ship Name")
    vgm_cutoff = fields.Datetime(string="VGM Cutoff")
    si_cutoff = fields.Datetime(string="SI Cutoff")
    doc_cutoff = fields.Datetime(string="Doc Cutoff")


    #Shipping
    sb_no = fields.Char("Shipping Bill")
    sb_date = fields.Date("Shipping Bill Date")

    actual_gate_open = fields.Datetime(string="Actual Gate Open")
    actual_gate_closed = fields.Datetime(string="Actual Gate Closed")
    
    container_pickup_time = fields.Datetime(string="Container Pickup Time")
    actual_gatein_time = fields.Datetime(string="Actual Gate In Time")


    gate_in_time = fields.Datetime(string="Gate In Time")
    vessel_load_time = fields.Datetime(string="Vessel Load Time")

    
    ship_arrival = fields.Datetime(string="Ship Arrival Date")
  
    @api.onchange("terminal_name")
    def set_domain_for_terminal_name(self):
            port = self.env['configuration.terminal.child'].search([('port_id', '=', self.ports.id)])
            # terminal = port.port_name
            # _logger.info("SAA " + str(terminal))
            terminal_ids = []
            
            for i in port:
                terminal_ids.append(i.id)
            # _logger.info(terminal_ids)
            result = { 
                            'domain': {'terminal_name': [ 
                            ('id', 'in', terminal_ids)] 
                            }
                        }
         
            return result
    
    @api.onchange("ports")
    def set_domain_for_terminal_name_using_port(self):
            port = self.env['configuration.terminal.child'].search([('port_id', '=', self.ports.id)])
            # terminal = port.port_name
            # _logger.info("SAA " + str(terminal))
            terminal_ids = []
            
            for i in port:
                terminal_ids.append(i.id)
                # _logger.info(i.terminals.port_name)
            # _logger.info(terminal_ids)
            result = { 
                            'domain': {'terminal_name': [ 
                            ('id', 'in', terminal_ids)] 
                            }
                        }
         
            return result
        

       