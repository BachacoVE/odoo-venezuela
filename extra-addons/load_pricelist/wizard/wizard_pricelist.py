# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    This Modules was developed by Netquatro, C.A. (<http://openerp.netquatro.com>)
#    Silver partner of Tiny.
#    author Javier Duran (<javier.duran@netquatro.com>) & 
#           Nhomar Hernandez (nhomar.hernandez@netquatro.com)
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import wizard
import pooler
from tools.translate import _

form = """<?xml version="1.0" encoding="utf-8"?>
<form string="Import price supplier list">
    <field name="file" filename="name"/>
    <newline/>
    <field name="name"/>
    <newline/>
</form>"""

fields = {
    'file': {'string': 'Price Supplier List File', 'type': 'binary', 'required': True},
    'name': {'string':"File name", 'type':'char', 'size':64, 'readonly':True},
}

result_form = """<?xml version="1.0"?>
<form string="Import price supplier list">
    <field name="state"/>
    <newline/>
    <separator string="Import result of price supplier list:" colspan="6"/>
    <field name="note" colspan="6" nolabel="1"/>
</form>"""
result_fields = {
    'state': {'string':"Result", 'type':'char', 'size':64, 'readonly':True},
    'note' : {'string':'Log', 'type':'text'},
}


class wiz_price_supp_list(wizard.interface):

    def _get_defaults(self, cr, uid, data, context={}):
#        config_ids = pooler.get_pool(cr.dbname).get('account.payment.epassporte.import.config').search(cr, uid, [])
#        if len(config_ids):
#            data['form']['config_id'] = config_ids[0]
#        else:
#            raise wizard.except_wizard(_('Warning'), _('You must define an ePassporte configuration.'))
        return data['form']


    def _import(obj, cr, uid, data, context={}):
        pool = pooler.get_pool(cr.dbname)
#        statement_obj = pool.get('account.bank.statement')
#        (note, state) = statement_obj.epassporte_import(cr, uid, data['id'], data['form']['file'], data['form']['name'], data['form']['config_id'], context=context)
#        return {'note':note, 'state':state}
        return {}


    states = {
        'init': {
            'actions': [_get_defaults],
            'result': {
                'type': 'form',
                'arch': form,
                'fields': fields,
                'state': [
                    ('end', 'Cancel', 'gtk-cancel'),
                    ('import', 'Import', 'gtk-ok', True),
                ],
            },
        },
        'import': {
            'actions': [_import],
            'result' : {'type' : 'form',
                        'arch' : result_form,
                        'fields' : result_fields,
                        'state' : [('end', 'Ok','gtk-ok') ] }
        },
    }

wiz_price_supp_list('price_sup_list')
