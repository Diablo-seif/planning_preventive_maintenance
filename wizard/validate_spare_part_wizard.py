from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class ValidateSparePartWizard(models.TransientModel):
    _name = 'validate.spare.part.wizard'
    _description = 'Wizard to validate and consume spare parts'

    maintenance_request_id = fields.Many2one('maintenance.request', string="Request")
    line_ids = fields.One2many('validate.spare.part.wizard.line', 'wizard_id', string="Spare Parts")

    def action_confirm(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("Please add at least one product."))

        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
        if not warehouse:
            raise UserError(_("No warehouse found. Please configure a warehouse first."))

        stock_location = warehouse.lot_stock_id
<<<<<<< HEAD
        
        source_location = self.env['stock.location'].search([
            ('usage', '=', 'production'),
        ], limit=1)
        if not source_location:
            source_location = self.env['stock.location'].search([
                ('usage', '=', 'inventory'),
            ], limit=1)
        if not source_location:
            raise UserError(_("No virtual source location found. Please check your stock locations."))
=======

        inventory_location = self.env['stock.location'].search([
            ('usage', '=', 'inventory'),
            ('company_id', '=', self.env.company.id)
        ], limit=1)

        if not inventory_location:
            raise UserError(_("No virtual inventory location found. Please check your stock locations."))
>>>>>>> 071c169 (Update V2)

        for line in self.line_ids:
            product = line.product_id
            if not product:
                raise UserError(_("Product %s has no variant defined.") % line.product_id.name)

            if line.quantity > 0:
                scrap = self.env['stock.scrap'].create({
                    'product_id': product.id,
                    'scrap_qty': line.quantity,
                    'product_uom_id': product.uom_id.id,
                    'location_id': stock_location.id,
                    'origin': self.maintenance_request_id.name or 'Maintenance',
                })
                scrap.action_validate()

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
                    'location_id': inventory_location.id,
                    'location_dest_id': stock_location.id,
                    'origin': self.maintenance_request_id.name or 'Maintenance',
                    'move_ids': [(0, 0, {
                        'name': _('Return Spare Part: %s') % product.name,
                        'product_id': product.id,
                        'product_uom_qty': return_qty,
                        'product_uom': product.uom_id.id,
                        'location_id': inventory_location.id,
                        'location_dest_id': stock_location.id,
                    })],
                })

                picking.action_confirm()
<<<<<<< HEAD

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

=======
>>>>>>> 071c169 (Update V2)
                picking.button_validate()

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

    wizard_id = fields.Many2one(comodel_name="validate.spare.part.wizard", )
    product_id = fields.Many2one('product.product',
            string="Product",
            domain=[('spare_parts_ok', '=', True)],
            required=True
        )
    quantity = fields.Float(string="Quantity", default=0.0)
    qty_available = fields.Float(
        string='On Hand',
        compute='_compute_qty_available',
    )
    difference = fields.Float(
        string='After Consumption',
        compute='_compute_difference',
    )
<<<<<<< HEAD
    
=======
>>>>>>> 071c169 (Update V2)

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
            if line.quantity > 0:
                if line.qty_available <= 0:
                    raise ValidationError(_("You don't have enough stock for %s.") % line.product_id.name)
                if line.quantity > line.qty_available:
                    raise ValidationError(
                        _("Quantity for %s must be less than or equal to on-hand stock.") % line.product_id.name)

            if line.quantity == 0:
                raise ValidationError(_("Please enter a valid quantity for %s.") % line.product_id.name)


