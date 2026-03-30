from odoo import api, fields, models
from odoo.exceptions import ValidationError

class MaintenanceEquipmentPlan (models.Model):
    _name = 'maintenance.equipment.plan'
    _description = "Plan for Maintenance Equipment"
    _order = 'done asc, task_duration asc'

    maintenance_equipment_id = fields.Many2one(
        comodel_name="maintenance.equipment",
        string="Maintenance Request",
    )
    user_id = fields.Many2one('res.users', 'User', readonly=True)

    tasks = fields.Char(
        string="Tasks",
    )

    interval = fields.Float(string="Interval",  required=False )
    different = fields.Float(string="Difference", required=False)

    task_duration = fields.Float(string="Task Duration" )

    unit_measure = fields.Selection(related='maintenance_equipment_id.reading_unit_of_measure', string="Unit Measure", readonly=True)

    product_ids = fields.Many2many(
        comodel_name='product.template',
        string="Spare Parts",
        domain=[('spare_parts_ok', '=', True)]
    )
    to_day = fields.Date(string="To Day", readonly=True)
    done = fields.Boolean(string="Done",  default=False)
