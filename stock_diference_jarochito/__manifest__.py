# -*- coding: utf-8 -*-
{
    'name': "stock_diference_jarochito",

    'summary': """
        Diferencia ventas de POS""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Xmarts",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale','stock','product','credit_limit_alert','hr','tracking','report_qweb_element_page_visibility'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'report/reporte_corte_inventario.xml',
        'report/corte_de_caja.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}