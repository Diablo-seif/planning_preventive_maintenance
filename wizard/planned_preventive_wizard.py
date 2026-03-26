from email.policy import default

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date


class PlannedPreventive(models.TransientModel):
    _name = 'planned.preventive.wizard'  # تأكد إن الاسم ده مطابق تماماً للي في الـ XML
    _description = 'Planned Preventive wizard'

    name = fields.Date(string="To Day", default=lambda self: date.today())
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user, readonly=True)
    preventive_maintenance_plan_ids = fields.One2many(comodel_name="preventive.maintenance.plan",
                                                      inverse_name="equipment_readings_id", string="Reading",
                                                      required=False, )
    product_ids = fields.Many2many(
        comodel_name='product.template',
        string="Spare Parts",
        domain=[('spare_parts_ok', '=', True)]
    )
    tasks = fields.Char(string="Tasks", required=True)
    task_duration = fields.Float(string="Task Duration", required=False)
    interval = fields.Float(string="Interval", required=False)


    # def action_apply(self):
    #     for line in self.preventive_maintenance_plan_ids:
    #         vals = {}
    #         if self.tasks:
    #             vals['tasks'] = self.tasks
    #         if self.interval:
    #             vals['interval'] = self.interval
    #         if self.task_duration:
    #             vals['task_duration'] = self.task_duration
    #         if self.product_ids:
    #             vals['product_ids'] = [(6, 0, self.product_ids.ids)]
    #         if vals:
    #             line.write(vals)

    def action_apply(self):
        for line in self.preventive_maintenance_plan_ids:
            vals = {}
            if self.tasks:
                vals['tasks'] = self.tasks
            if self.interval:
                vals['interval'] = self.interval
            if self.task_duration:
                vals['task_duration'] = self.task_duration
            if self.product_ids:
                vals['product_ids'] = [(6, 0, self.product_ids.ids)]
            if vals:
                line.write(vals)

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_confirm(self):
        for wizard in self:
            for line in wizard.preventive_maintenance_plan_ids:
                # إنشاء سجل دائم في خطة صيانة المعدة
                self.env['maintenance.equipment.plan'].create({
                    'maintenance_equipment_id': line.equipment_id.id,
                    'tasks': line.tasks,
                    'interval': line.interval,
                    'task_duration': line.task_duration,
                    'different': line.different,
                    'product_ids': [(6, 0, line.product_ids.ids)],
                    'user_id': wizard.user_id.id,
                    'to_day': line.to_day,
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
    different = fields.Float(compute='_compute_different', string="Difference", required=False, store=True)

    product_ids = fields.Many2many(
        comodel_name='product.template',
        string="Spare Parts",
        domain=[('spare_parts_ok', '=', True)]
    )
    to_day = fields.Date(string="To Day", default=lambda self: date.today())

    @api.depends('task_duration', 'interval')
    def _compute_different(self):
        for rec in self:
            rec.different = rec.task_duration - rec.interval
