from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date


class EquipmentReadings(models.TransientModel):
    _name = 'equipment.readings.wizard'
    _description = 'Equipment Readings Wizard'

    name = fields.Date(string="To Day", default=lambda self: date.today())
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user, readonly=True)
    read_line_ids = fields.One2many(comodel_name="read.line", inverse_name="equipment_readings_id", string="Reading", required=False, )

    def action_confirm(self):
        for wizard in self:
            for line in wizard.read_line_ids:
                self.env['maintenance.equipment.readings'].create({
                    'maintenance_equipment_id': line.equipment_id.id,
                    'reading': line.reading,
                    'user_id': line.user_id.id,
                    'name': line.name,
                })
        return {'type': 'ir.actions.act_window_close'}

class ReadLines(models.TransientModel):
    _name = 'read.line'
    _description = "Read Line"

    equipment_readings_id = fields.Many2one(comodel_name="equipment.readings.wizard", string="Reading")

    equipment_id = fields.Many2one(comodel_name="maintenance.equipment", string="Equipments",required=True)
    unit_measure = fields.Selection(related='equipment_id.reading_unit_of_measure', string="Unit Measure", readonly=True)
    user_id = fields.Many2one(related='equipment_readings_id.user_id',)
    reading = fields.Float(string="Reading",  required=False )
    name = fields.Date(string="To Day", default=lambda self: date.today())



