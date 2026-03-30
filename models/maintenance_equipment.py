from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date, timedelta, datetime, time


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    reading_unit_of_measure = fields.Selection([
        ('hours', 'Hours'),
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('years', 'Years'),
        ('kilometers', 'KiloMeters'),
    ],
        default='days',
        string='Type of Maintenance',
        required=True,

    )

    maintenance_equipment_plan_ids = fields.One2many(
        comodel_name="maintenance.equipment.plan",
        inverse_name="maintenance_equipment_id",
    )

    maintenance_equipment_reading_ids = fields.One2many(
        comodel_name="maintenance.equipment.readings",
        inverse_name="maintenance_equipment_id",
    )
    reading = fields.Float(string="Reading", compute="_compute_max_reading", required=False, store=True)

    @api.depends('maintenance_equipment_reading_ids', 'maintenance_equipment_reading_ids.reading')
    def _compute_max_reading(self):
        for equipment in self:
            readings = equipment.maintenance_equipment_reading_ids.mapped('reading')
            equipment.reading = max(readings) if readings else 0.0

    def maintenance_request_plans(self):
        today = fields.Date.today()
        scheduled_dt = datetime.combine(today, time(9, 0, 0))
        admin_user = self.env.ref('base.user_admin')
        target_domain = [
            ('maintenance_equipment_plan_ids', '!=', False),
            ('maintenance_equipment_plan_ids.done', '=', False),
        ]
        records_to_update = self.search(target_domain)

        if not records_to_update:
            return True
        for request in records_to_update:

            sorted_plans = request.maintenance_equipment_plan_ids.sorted(
                key=lambda p: (p.done, p.task_duration)
            )

            for plan in sorted_plans:

                if plan.done:
                    continue

                elif not plan.done:
                    alert_start_limit = plan.task_duration - plan.interval
                    # plan.interval <= plan.task_duration
                    if request.reading >= alert_start_limit:
                        spare_ordered_ids = [
                            (0, 0, {'product_id': line.id})
                            for line in plan.product_ids
                        ]

                        request.env["maintenance.request"].sudo().create({
                            'name': plan.tasks,
                            'maintenance_for': 'equipment',
                            'equipment_id': request.id,
                            'maintenance_type': 'preventive',
                            'user_id': admin_user.id,
                            'spare_ordered_ids': spare_ordered_ids,
                            'duration': 1.0,
                            'schedule_date': scheduled_dt,
                            'request_date': today,
                        })
                        plan.done = True

                    else:
                        break
                else:
                    break
        return True
