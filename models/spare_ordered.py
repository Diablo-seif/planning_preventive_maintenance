from odoo import api, fields, models, _


class SpareOrdered(models.Model):
    _name = 'spare.ordered'
    _description = 'Spare Ordered'

    maintenance_request_id = fields.Many2one(
        comodel_name="maintenance.request",
        string="Maintenance Request",
    )

    product_id = fields.Many2one('product.product', string="Product", domain=[('spare_parts_ok', '=', True)],
                                 readonly=True)

    quantity = fields.Float(string="Quantity", default=1)
    need = fields.Boolean(default=True, readonly=False)

<<<<<<< HEAD
    product_id = fields.Many2one('product.template', string="Product", domain=[('spare_parts_ok', '=', True)], readonly=True)
    quantity = fields.Float(string="Quantity")
    need = fields.Boolean(default=True,readonly=False)
=======
>>>>>>> 071c169 (Update V2)

