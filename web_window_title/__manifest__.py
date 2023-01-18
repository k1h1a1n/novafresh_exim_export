# -*- coding: utf-8 -*-
{
    'license': 'LGPL-3',
    'name': "White Label",
    'summary': "The custom whitelabel module for berm",
    'author': "saif kazi",
    'website': "",
    'support': '',
    'category': 'Extra Tools',
    'version': '1.1',
    'depends': ['base_setup'],
    'demo': [
        'data/demo.xml',
    ],
    'qweb':[
       "static/src/xml/base.xml",
    ],
    'data': [
        'views/webclient_templates.xml',
        'views/res_config.xml',
        'data/mail_template.xml'
    ],
    'images': [
        'static/description/main_screenshot.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}