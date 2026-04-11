from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date
from odoo.fields import Command


class PlannedPreventive(models.TransientModel):
    _name = 'planned.preventive.wizard'
    _description = 'Planned Preventive wizard'

    name = fields.Date(string="To Day", default=lambda self: date.today())
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user, readonly=True)
    preventive_maintenance_plan_ids = fields.One2many(comodel_name="preventive.maintenance.plan",
                                                      inverse_name="equipment_readings_id", string="Reading",
                                                      required=False, )
    equipment_ids = fields.Many2many(comodel_name="maintenance.equipment", string="Equipments", )

    product_ids = fields.Many2many(
        comodel_name='product.product',
        string="Spare Parts",
        domain=[('spare_parts_ok', '=', True)]
    )

    tasks = fields.Char(string="Tasks", required=True, default="New")
    task_duration = fields.Float(string="Task Duration", required=False)
    interval = fields.Float(string="Interval", required=False)
    different = fields.Float(compute='_compute_different', string="Difference", required=False)

    @api.depends('task_duration', 'interval')
    def _compute_different(self):
        for rec in self:
            rec.different = rec.task_duration - rec.interval


    def action_confirm(self):
        for rec in self:
            for line in rec.preventive_maintenance_plan_ids:

                self.env['maintenance.equipment.plan'].create({
                    'maintenance_equipment_id': line.equipment_id.id,
                    'tasks': line.tasks,
                    'interval': line.interval,
                    'task_duration': line.task_duration,
                    'different': line.different,
                    'product_ids': [Command.set(line.product_ids.ids)],
                    'user_id': rec.user_id.id,
                    'name': line.name,
                })
        return {'type': 'ir.actions.act_window_close'}

    def action_confirm_group(self):
        for rec in self:
            for line in rec.equipment_ids:
                self.env['maintenance.equipment.plan'].create({
                    'maintenance_equipment_id': line.id,
                    'tasks': rec.tasks,
                    'interval': rec.interval,
                    'task_duration': rec.task_duration,
                    'different': rec.different,
                    'product_ids': [Command.set(rec.product_ids.ids)],
                    'user_id': rec.user_id.id,
                    'name': rec.name,
                })
        return {'type': 'ir.actions.act_window_close'}





class PreventiveMaintenancePlan(models.TransientModel):
    _name = 'preventive.maintenance.plan'
    _description = 'Preventive Maintenance Plan'

    equipment_readings_id = fields.Many2one(comodel_name="planned.preventive.wizard", string="Reading")

    equipment_id = fields.Many2one(comodel_name="maintenance.equipment", string="Equipment", required=True, )
    unit_measure = fields.Selection(related='equipment_id.reading_unit_of_measure', string="Unit Measure",
                                    readonly=True)
    user_id = fields.Many2one(related='equipment_readings_id.user_id')
    tasks = fields.Char(string="Tasks", required=True, default="New")
    task_duration = fields.Float(string="Task Duration", required=False)
    interval = fields.Float(string="Interval", required=False)
    different = fields.Float(compute='_compute_different', string="Difference", required=False)

    product_ids = fields.Many2many(
        comodel_name='product.product',
        string="Spare Parts",
        domain=[('spare_parts_ok', '=', True)]
    )

    name = fields.Date(string="To Day", default=lambda self: date.today())

    @api.depends('task_duration', 'interval')
    def _compute_different(self):
        for rec in self:
            rec.different = rec.task_duration - rec.interval


