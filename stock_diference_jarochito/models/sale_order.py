from odoo import models, fields
from ast import literal_eval
from odoo.tests import  Form

class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_confirm = fields.Boolean(
        string="Venta Confirmada",
        default=False
    )

    def button_automizate_confirm_orders(self):
        for rec in self:
            stock_picking = self.env['stock.picking'].search([
                ('sale_id', '=', rec.id),
                ('state', '!=', 'done')
            ])
            for stocks in stock_picking:
                wiz = stocks.button_validate()
                wiz = Form(self.env['stock.immediate.transfer'].with_context(wiz['context'])).save().process()
            return rec
        # self.sale_confirm = True
