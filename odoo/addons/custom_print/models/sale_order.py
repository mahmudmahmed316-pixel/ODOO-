from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_custom_print_cog(self):
        """Action for the gear icon on the form."""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Custom Print Status / حالة الطباعة الخاصة'),
                'message': _('This feature allows you to print the Bilingual Commercial Invoice. / هذه الميزة تسمح لك بطباعة الفاتورة التجارية ثنائية اللغة.'),
                'sticky': False,
                'type': 'info',
            }
        }

    def action_print_commercial_invoice_report(self):
        """Method to trigger the commercial invoice report."""
        return self.env.ref('custom_print.action_report_commercial_invoice').report_action(self)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_custom_print_cog(self):
        """Action for the gear icon on the form."""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Custom Print Status / حالة الطباعة الخاصة'),
                'message': _('This feature allows you to print the Bilingual Commercial Invoice. / هذه الميزة تسمح لك بطباعة الفاتورة التجارية ثنائية اللغة.'),
                'sticky': False,
                'type': 'info',
            }
        }
