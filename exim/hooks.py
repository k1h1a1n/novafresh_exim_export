from odoo import api, SUPERUSER_ID

def uninstall_hook(cr,registry):
    env = api.Environment(cr,SUPERUSER_ID,{})
    env['exim.shipments'].search([]).unlink()
    env['exim.shipments.ci'].search([]).unlink()
    