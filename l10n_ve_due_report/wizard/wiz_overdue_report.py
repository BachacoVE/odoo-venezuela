# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
#                    Javier Duran <javier@vauxoo.com>
# 
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

'''
Fiscal Report For Venezuela
'''

from osv import fields
from osv import osv
import time
import ir
from mx import DateTime
import datetime
import pooler
from tools import config
import wizard
import netsvc


book_form= """<?xml version="1.0"?>
<form string="Analisis de cuentas por cobrar.">
     <label string="
     AYUDA: 
     Usted va a imprimir un reporte con todos los estados de cuenta de todos sus cliente\n
     Este estado de cuenta hará un análisis hacia atrás de las facturas pendientes\n
     por pagar de dicho cliente desde el momento de su facturación." colspan="4"/>
     <newline/>
     <newline/>
     <field name="date_start" string="Fecha de Comienzo del Análisis" col="2"/>
     <field name="type_report" string="Tipo de Reporte" col="2"/>
</form>
"""

book_field= {
    'date_start': {'string':'Start Date','type':'date','required': True},
#    'date_end': {'string':'End Date','type':'date','required': True},
    'type_report':{'string':"Type of Report", 'type':'selection', 'selection':[('cxc','Cuentas por Cobrar'),('cxp','Cuentas por Pagar'),('both','Ambas')]},
}
    
def _get_default(self, cr, uid, data, context):
    """
    Process a data

    @param cr: cursor to database
    @param user: id of current user
    @param data: dict that contains data about wizard, and internal variables
    @param context: context arguments, like lang, time zone

    @return: {}
    """
    data['form']['date_start'] = time.strftime('%Y-%m-%d')
    data['form']['type_report'] = 'cxc'
    return data['form']

class wiz_overdue_report(wizard.interface):
    '''
    Wizzard invoice list
    '''
    states = {
        'init' : {
            'actions' : [_get_default],
            'result' : {'type' : 'form',
                    'arch' : book_form,
                    'fields' : book_field,
                    'state' : [('end', 'Cancel','gtk-cancel'),('print_report', 'Print Report','gtk-print') ]}
        },
        'print_report' : {
            'actions' : [],
            'result' : {'type' : 'print',
                   'report':'reports.overdue_report',
                    'state' : 'end'}
        },
    }
    
    
wiz_overdue_report("wizard.overdue_report")
