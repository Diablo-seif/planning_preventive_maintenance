from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date


class EquipmentReadings(models.Model):
    _name = 'maintenance.equipment.readings'
    _description = 'Equipment Readings'

    maintenance_equipment_id = fields.Many2one(
        comodel_name="maintenance.equipment",
        string="Maintenance Request",
    )

    unit_measure = fields.Selection(related='maintenance_equipment_id.reading_unit_of_measure', string="Unit Measure",
                                    readonly=True)
    user_id = fields.Many2one('res.users', 'User', readonly=True)
    reading = fields.Float(string="Reading")
    name = fields.Date(string="To Day")
