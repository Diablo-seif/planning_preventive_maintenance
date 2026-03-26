from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    spare_parts_ok = fields.Boolean(string='Spare Part')

    @api.onchange('type','is_storable')
    def onchange_spare_parts_ok(self):
        for product in self:
            if product.type != 'consu' or product.is_storable != True :
                product.spare_parts_ok = False

