from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    spare_parts_ok = fields.Boolean(string='Spare Part')

    @api.onchange('type','is_storable')
    def onchange_spare_parts_ok(self):
        for product in self:
            if product.type != 'consu' or product.is_storable != True :
                product.spare_parts_ok = False

    @api.constrains('type', 'is_storable', 'spare_parts_ok')
    def check_spare_parts_ok(self):
        for product in self:
            if product.is_storable != True and product.spare_parts_ok:
                raise ValidationError(_('This product does not track inventory.'))

            elif product.type != 'consu'and product.spare_parts_ok:
                raise ValidationError(_('This product must be a storable product.'))


