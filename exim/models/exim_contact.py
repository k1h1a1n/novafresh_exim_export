from odoo import models, fields ,api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class EximContacts(models.Model):
    _inherit = 'res.partner'

    prefix = fields.Char("Prefix",required=True)
    suffix = fields.Char("Suffix") 
    beneficiary_name = fields.Text("Beneficiary Name")
    bank_name = fields.Text("Bank Name")
    bank_address = fields.Text("Bank Address")
    branch = fields.Char("Branch")
    swift_code = fields.Char("Swift Code")
    ad_code = fields.Char("AD Code")
    ifsc_code = fields.Char("IFSC Code")
    ac_no = fields.Char("A/C No")
    iban = fields.Char("IBAN")

    intermediatory_beneficiary_name = fields.Text("Beneficiary Name")
    intermediatory_bank_name = fields.Text("Bank Name")
    intermediatory_bank_address = fields.Text("Bank Address")
    intermediatory_branch = fields.Char("Branch")
    intermediatory_swift_code = fields.Char("Swift Code")
    intermediatory_iban = fields.Char("IBAN")



class EximContactsTags(models.Model):
    _inherit = 'res.partner.category'

   
    
    
    # def create(self, values):
    #     if values.name == "Consignee":
    #         raise ValidationError("Consignee already Exist")
        
    #     if values.name == "Shipper":
    #         raise ValidationError("Shipper already Exist")
        
    #     return super(EximContactsTags, self).create(values)

    
    def unlink(self):
        # _logger.info(self.id)
        if self.name == "Consignee" or self.name == "Shipper":
            raise ValidationError("Cannot Delete the record")
        
        return super(EximContactsTags, self).unlink() 