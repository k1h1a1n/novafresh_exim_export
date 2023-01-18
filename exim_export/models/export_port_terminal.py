from odoo import models, fields ,api
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class ExportPortTerminal(models.Model):
    _inherit = 'configuration.port.child'

    terminals = fields.One2many('configuration.terminal.child','port_id',string="Terminals")


class ExportPortTerminalName(models.Model):
    _name = 'configuration.terminal.child'
    _rec_name = 'port_name'

    port_id = fields.Many2one("configuration.port.child",string="Port ID")
    port_name = fields.Char("Terminal Name")
