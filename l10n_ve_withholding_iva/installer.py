# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Nhomar Hernandez <nhomar@vauxoo.com>
#
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
from osv import osv
from osv import fields
from tools.translate import _
import addons
import base64

class wh_vat_installer(osv.osv_memory):
    """
    wh_vat_installer
    """
    _name='l10n_ve_withholding_iva.installer'
    _inherit = 'res.config.installer'
    _description = __doc__
    
    def default_get(self, cr, uid, fields, context=None):
        data = super(wh_vat_installer, self).default_get(cr, uid, fields, context=context)
        gaceta = open(addons.get_module_resource('l10n_ve_withholding_iva','files', 'RegimendeRetencionesdelIVA.odt'),'rb')
        data['gaceta'] = base64.encodestring(gaceta.read())
        return data
    
    _columns = {
        'name':fields.char('First Data', 34),
        'gaceta':fields.binary('Law related', readonly=True, help="Law related where we are referencing this module"),
        'description':fields.text('Description', readonly=True),
        'wh':fields.boolean('Are You Withholding Agent?'),
    }
    
    _defaults = {
        'name' : 'RegimendeRetencionesdelIVA.odt',
        'description' : """
        Create a Journal
        Do this and This and This.
        """
    }
wh_vat_installer()
