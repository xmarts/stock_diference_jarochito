# -*- coding: utf-8 -*-
{
    'name': "Diferencias de Stock",
    'author': "Xmarts",
    'website': "http://www.erp.xmarts.com",
    'category': 'Stock, Delivery',
    'version': '15.0',
    'depends': ['base', 'stock', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/stock_picking.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
