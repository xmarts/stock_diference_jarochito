# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class stock_diference_jarochito(models.Model):
#     _name = 'stock_diference_jarochito.stock_diference_jarochito'
#     _description = 'stock_diference_jarochito.stock_diference_jarochito'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
