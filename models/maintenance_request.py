from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    maintenance_request_line_ids = fields.One2many(
        comodel_name="maintenance.request.line",
        inverse_name="maintenance_request_id",
    )

    spare_ordered_ids = fields.One2many(
        comodel_name="spare.ordered",
        inverse_name="maintenance_request_id",
    )

    reading_unit_of_measure = fields.Selection(
        related="equipment_id.reading_unit_of_measure",
        string="Category of Maintenance ", )

    expected_mtbf = fields.Integer(
        related="equipment_id.expected_mtbf",
        string="Expected Mean Time Between Failure", )

    tasks = fields.Text(
        string="Tasks",
        required=False, )

    def action_go_validate_spare_part(self):
        self.ensure_one()
        spare_ordered_ids = [
            (0, 0, {
                'product_id': line.product_id.id,

            }) for line in self.spare_ordered_ids if line.product_id and  line.need  ]

        self.spare_ordered_ids.write({'need': False})


        return {
            'type': 'ir.actions.act_window',
            'name': 'Select Spare Parts',
            'res_model': 'validate.spare.part.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_maintenance_request_id': self.id,
                'default_quantity': 1,
                'default_line_ids': spare_ordered_ids,
            }
        }



class MaintenanceRequestLines(models.Model):
    _name = 'maintenance.request.line'
    _description = 'Maintenance Request Line'

    maintenance_request_id = fields.Many2one(
        comodel_name="maintenance.request",
        string="Maintenance Request",
    )

    done = fields.Boolean(default=False, readonly=True)



    product_id = fields.Many2one('product.product', string="Product", domain=[('spare_parts_ok', '=', True)], )

    quantity = fields.Float(string="Quantity", default=1.0)
    qty_available = fields.Float(
        'On Hand', compute='_compute_qty_available', )

    difference = fields.Float(
        string='After Consumption',
        compute='_compute_difference',
    )

    @api.depends('product_id', 'quantity')
    def _compute_qty_available(self):
        for line in self:
            line.qty_available = line.product_id.qty_available if line.product_id else 0.0

    @api.depends('product_id', 'quantity')
    def _compute_difference(self):
        for line in self:
            line.difference = line.qty_available - line.quantity if line.quantity and line.qty_available else 0.0
<<<<<<< HEAD
=======

>>>>>>> 071c169 (Update V2)
