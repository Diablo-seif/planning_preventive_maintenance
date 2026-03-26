from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class ValidateSparePartWizard(models.Model):
    _name = 'validate.spare.part.wizard'
    _description = 'Wizard to validate and consume spare parts'

    maintenance_request_id = fields.Many2one('maintenance.request', string="Request")
    line_ids = fields.One2many('validate.spare.part.wizard.line', 'wizard_id', string="Spare Parts")

    # def action_confirm(self):
    #     self.ensure_one()
    #     if not self.line_ids:
    #         raise UserError(_("Please add at least one product."))
    #
    #
    #     for line in self.line_ids:
    #         product = line.product_id
    #         product_product = product.product_variant_id
    #         if not product_product:
    #             raise UserError(_("Product %s has no variant defined.") % product.name)
    #
    #         scrap = self.env['stock.scrap'].create({
    #             'product_id': product_product.id,
    #             'product_uom_id': product_product.uom_id.id,
    #             'scrap_qty': line.quantity,
    #             'origin': self.maintenance_request_id.name or 'Maintenance',
    #         })
    #         scrap.action_validate()
    #
    #
    #         self.env['maintenance.request.line'].create({
    #             'maintenance_request_id': self.maintenance_request_id.id,
    #             'product_id': product.id,
    #             'quantity': line.quantity,
    #             'qty_available': line.qty_available,
    #             'done': True,
    #         })
    #
    #     return {'type': 'ir.actions.act_window_close'}

    def action_confirm(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("Please add at least one product."))

        warehouse = self.env['stock.warehouse'].search([], limit=1)
        if not warehouse:
            raise UserError(_("No warehouse found. Please configure a warehouse first."))

        stock_location = warehouse.lot_stock_id  # المخزن الرئيسي

        # ✅ البحث عن الموقع الافتراضي ديناميكياً بدلاً من env.ref
        source_location = self.env['stock.location'].search([
            ('usage', '=', 'production'),
        ], limit=1)
        if not source_location:
            # fallback: موقع التعديلات المخزنية الافتراضي
            source_location = self.env['stock.location'].search([
                ('usage', '=', 'inventory'),
            ], limit=1)
        if not source_location:
            raise UserError(_("No virtual source location found. Please check your stock locations."))

        for line in self.line_ids:
            # ====== استخراج المنتج بشكل صحيح ======
            product = line.product_id
            if product._name == 'product.template':
                product = product.product_variant_id
            if not product:
                raise UserError(
                    _("Product %s has no variant defined.") % line.product_id.name
                )

            # ====== 1. كمية موجبة → صرف من المخزن (Scrap) ======
            if line.quantity > 0:
                scrap = self.env['stock.scrap'].create({
                    'product_id': product.id,
                    'scrap_qty': line.quantity,
                    'product_uom_id': product.uom_id.id,
                    'location_id': stock_location.id,
                    'origin': self.maintenance_request_id.name or 'Maintenance',
                })
                scrap.action_validate()

            # ====== 2. كمية سالبة → إرجاع للمخزن ======
            elif line.quantity < 0:
                return_qty = abs(line.quantity)

                picking_type = self.env['stock.picking.type'].search([
                    ('code', '=', 'incoming'),
                    ('warehouse_id', '=', warehouse.id),
                ], limit=1)
                if not picking_type:
                    raise UserError(_("No incoming picking type found for the warehouse."))

                picking = self.env['stock.picking'].create({
                    'picking_type_id': picking_type.id,
                    'location_id': source_location.id,
                    'location_dest_id': stock_location.id,
                    'origin': self.maintenance_request_id.name or 'Maintenance',
                    'move_ids': [(0, 0, {
                        'name': _('Return Spare Part: %s') % (
                                self.maintenance_request_id.name or ''),
                        'product_id': product.id,
                        'product_uom_qty': return_qty,
                        'product_uom': product.uom_id.id,
                        'location_id': source_location.id,
                        'location_dest_id': stock_location.id,
                    })],
                })

                picking.action_confirm()

                # إنشاء move_line يدوياً إذا لم تُنشأ تلقائياً
                if not picking.move_line_ids:
                    for move in picking.move_ids:
                        self.env['stock.move.line'].create({
                            'move_id': move.id,
                            'picking_id': picking.id,
                            'product_id': product.id,
                            'product_uom_id': product.uom_id.id,
                            'quantity': return_qty,
                            'location_id': source_location.id,
                            'location_dest_id': stock_location.id,
                        })
                else:
                    for ml in picking.move_line_ids:
                        ml.quantity = return_qty

                picking.button_validate()

            # ====== 3. تسجيل السطر في طلب الصيانة ======
            self.env['maintenance.request.line'].create({
                'maintenance_request_id': self.maintenance_request_id.id,
                'product_id': line.product_id.id,
                'quantity': line.quantity,
                'qty_available': line.qty_available,
                'done': True,
            })

        return {'type': 'ir.actions.act_window_close'}

class ValidateSparePartWizardLine(models.TransientModel):
    _name = 'validate.spare.part.wizard.line'
    _description = 'Wizard Spare Part Line'

    wizard_id = fields.Many2one('validate.spare.part.wizard')


    product_id = fields.Many2one(
        'product.template',
        string="Product",
        domain=[('spare_parts_ok', '=', True)],
    )
    quantity = fields.Float(string="Quantity")
    qty_available = fields.Float(
        string='On Hand',
        compute='_compute_qty_available',
    )
    difference = fields.Float(
        string='After Consumption',
        compute='_compute_difference',
    )
    #

    @api.depends('quantity', 'qty_available')
    def _compute_difference(self):
        for line in self:
            line.difference = line.qty_available - line.quantity

    @api.depends('product_id')
    def _compute_qty_available(self):
        for line in self:
            line.qty_available = line.product_id.qty_available if line.product_id else 0.0


    @api.constrains('quantity', 'qty_available')
    def check_quantity(self):
        for line in self:

            if line.qty_available == 0:
                raise ValueError("you don't have stock.")
            if line.qty_available < 0:
                raise ValueError("stock must be a positive number.")
            if line.quantity == 0:
                raise ValidationError("Quantity please.")

            if line.quantity > line.qty_available:
                raise ValidationError("Quantity must be under vals of stock.")
