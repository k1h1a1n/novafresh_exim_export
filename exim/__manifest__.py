{ 
 'name': "EXIM",
 'summary': "Export Import Business",
 'author': "Saif Kazi", 
 'website': "http://www.esehat.org", 
 'category': 'Exim', 
 'version': '13.0.1', 
 'depends': ['base','contacts','product','uom','mail','report_xlsx'], 
 'data': ['views/exim_conf.xml',
          'views/exim_import.xml',
          'views/exim_pi.xml',
          'views/exim_igm.xml',
          'views/exim_contact.xml',
          'views/exim_product.xml',
          'data/data.xml',
          'data/mail_template.xml',
          'security/groups.xml',
          'security/ir.model.access.csv',
          'report/exim_igm_action.xml',
          'report/exim_igm_report_template.xml',
          ],
 'uninstall_hook':'uninstall_hook'
} 