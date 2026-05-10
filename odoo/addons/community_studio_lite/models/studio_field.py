from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StudioCustomField(models.Model):
    _name = 'studio.custom.field'
    _description = 'Studio Custom Field Builder'

    name = fields.Char(string='Field Name', required=True, help="Technical name, will be prefixed with x_")
    field_label = fields.Char(string='Field Label', required=True)
    model_id = fields.Many2one('ir.model', string='Target Model', required=True, ondelete='cascade')
    ttype = fields.Selection([
        ('char', 'Text (Char)'),
        ('integer', 'Number (Integer)'),
        ('float', 'Decimal (Float)'),
        ('boolean', 'Checkbox (Boolean)'),
        ('date', 'Date'),
        ('datetime', 'Date & Time'),
        ('text', 'Long Text'),
        ('monetary', 'Money (Monetary)'),
    ], string='Field Type', default='char', required=True)
    
    target_view_id = fields.Many2one('ir.ui.view', string='Target View', 
                                    domain="[('model', '=', model_name), ('type', '=', 'form')]",
                                    help="Which view should show this field?")
    
    xpath_expression = fields.Char(string='XPath Expression', default="//group[1]",
                                  help="Where precisely to place the field. Default is in the first group.")
    
    position = fields.Selection([
        ('inside', 'Inside'),
        ('before', 'Before'),
        ('after', 'After'),
    ], string='Position', default='inside', required=True)

    model_name = fields.Char(related='model_id.model', store=True)
    state = fields.Selection([('draft', 'Draft'), ('active', 'Active')], default='draft')

    def action_apply_changes(self):
        for rec in self:
            # 1. Create the Field in ir.model.fields
            field_name = rec.name if rec.name.startswith('x_') else f'x_{rec.name}'
            
            existing_field = self.env['ir.model.fields'].search([
                ('model_id', '=', rec.model_id.id),
                ('name', '=', field_name)
            ])

            if not existing_field:
                self.env['ir.model.fields'].create({
                    'name': field_name,
                    'model_id': rec.model_id.id,
                    'field_description': rec.field_label,
                    'ttype': rec.ttype,
                    'state': 'manual', # Important: manual fields are stored in DB
                })

            # 2. Create the View Inheritance in ir.ui.view
            if rec.target_view_id:
                view_xml_id = f"community_studio_lite.custom_view_{rec.model_name.replace('.', '_')}_{field_name}"
                
                # Check if an inherited view for this field already exists
                existing_view = self.env['ir.ui.view'].search([
                    ('name', '=', f"Studio Override: {field_name}"),
                    ('inherit_id', '=', rec.target_view_id.id)
                ])

                arch = f'<xpath expr="{rec.xpath_expression}" position="{rec.position}">' \
                       f'<field name="{field_name}"/>' \
                       f'</xpath>'

                if not existing_view:
                    self.env['ir.ui.view'].create({
                        'name': f"Studio Override: {field_name}",
                        'model': rec.model_name,
                        'inherit_id': rec.target_view_id.id,
                        'arch': f'<data>{arch}</data>',
                        'priority': 99,
                    })
                else:
                    existing_view.arch = f'<data>{arch}</data>'

            # Force registry reload to apply changes immediately
            self.env.flush_all()
            self.env.registry.setup_models(self.env.cr)
            
            rec.state = 'active'
        return True
