{
    'name': "EXIM",
    'summary': "Export",
    'author': "Saif Kazi",
    'website': "http://www.esehat.org",
    'category': 'Exim',
    'version': '13.0.1',
    'depends': ['base','exim', 'account','contacts', 'product', 'uom', 'mail', 'sale','sale_management'],
    'data': [
        'report/invoice_inherited_report.xml',
        'report/export_invoice_novafresh_action.xml',
        'report/export_invoice_novafresh.xml',
        'views/export_dbk.xml',
        'views/export_sales_order.xml',
        'views/export_shipment.xml',
        'views/export_lot.xml',
        'views/export_terminal_conf.xml',
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/shipmentmail_export_template.xml',
        'views/inherited_sales_make_invoice.xml',
        'views/export_menu.xml',
    ]
}
