# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

import time
from report import report_sxw
from osv import osv
import pooler

class rep_comprobante(report_sxw.rml_parse):
    #Variables Globales----------------------------------------------------
    ttcompra        = 0
    ttcompra_sdcf   = 0
    ttretencion     = 0
    ttbase          = 0
    ttiva           = 0

    #---------------------------------------------------------------------

    def __init__(self, cr, uid, name, context):
        super(rep_comprobante, self).__init__(cr, uid, name, context)    
        self.localcontext.update({
            'time': time,
            'get_partner_addr': self._get_partner_addr,
            'get_alicuota': self._get_alicuota,
            'get_tipo_doc': self._get_tipo_doc,
            'get_totales': self._get_totales,
            'get_tot_gral_compra': self._get_tot_gral_compra,
            'get_tot_gral_compra_scf': self._get_tot_gral_compra_scf,
            'get_tot_gral_base': self._get_tot_gral_base,
            'get_tot_gral_iva': self._get_tot_gral_iva,
            'get_tot_gral_retencion': self._get_tot_gral_retencion
        })

    def _get_partner_addr(self, idp=None):
        if not idp:
            return []

        addr_obj = self.pool.get('res.partner.address')
        addr_inv = 'NO HAY DIRECCION FISCAL DEFINIDA'
        addr_ids = addr_obj.search(self.cr,self.uid,[('partner_id','=',idp), ('type','=','invoice')])
        if addr_ids:                
            addr = addr_obj.browse(self.cr,self.uid, addr_ids[0])
            addr_inv = (addr.street or '')+' '+(addr.street2 or '')+' '+(addr.zip or '')+ ' '+(addr.city or '')+ ' '+ (addr.country_id and addr.country_id.name or '')+ ', TELF.:'+(addr.phone or '')
        return addr_inv 


    def _get_alicuota(self, tnom=None):
        if not tnom:
            return []

        tax_obj = self.pool.get('account.tax')
        tax_ids = tax_obj.search(self.cr,self.uid,[('name','=',tnom)])[0]
        tax = tax_obj.browse(self.cr,self.uid, tax_ids)

        return tax.amount*100


    def _get_tipo_doc(self, tipo=None):
        if not tipo:
            return []

        types = {'out_invoice': 'F', 'in_invoice': 'F', 'out_refund': 'C', 'in_refund': 'C'}

        return types[tipo]



    def _get_totales(self, comp_id):        
        if not comp_id:
            return []

        types = {'out_invoice': 's', 'in_invoice': 's', 'out_refund': 'r', 'in_refund': 'r'}
        tot_comp = {}
        tot_comp_sdc = {}
        tot_base_imp = {}
        tot_imp_iva = {}
        tot_iva_ret = {}

        comp_obj = self.pool.get('account.retention')
        comp = comp_obj.browse(self.cr,self.uid, comp_id)
        res = {}
        ttal = {}

        for rl in comp.retention_line:
            print 'sin credito fiscal: ',rl.invoice_id.sin_cred
            if rl.invoice_id.sin_cred:
                tot_comp_sdc[types[rl.invoice_id.type]] = tot_comp_sdc.get(types[rl.invoice_id.type],0.0) + rl.invoice_id.amount_total
            else:
                tot_comp[types[rl.invoice_id.type]] = tot_comp.get(types[rl.invoice_id.type],0.0) + rl.invoice_id.amount_total
            for txl in rl.invoice_id.tax_line:
                tot_base_imp[types[rl.invoice_id.type]] = tot_base_imp.get(types[rl.invoice_id.type],0.0) + txl.base_ret
                tot_imp_iva[types[rl.invoice_id.type]] = tot_imp_iva.get(types[rl.invoice_id.type],0.0) + txl.amount
                tot_iva_ret[types[rl.invoice_id.type]] = tot_iva_ret.get(types[rl.invoice_id.type],0.0) + txl.amount_ret


        self.ttcompra = tot_comp.get('s',0.0) - tot_comp.get('r',0.0)
        self.ttcompra_sdcf = tot_comp_sdc.get('s',0.0) - tot_comp_sdc.get('r',0.0)
        self.ttbase = tot_base_imp.get('s',0.0) - tot_base_imp.get('r',0.0)
        self.ttiva = tot_imp_iva.get('s',0.0) - tot_imp_iva.get('r',0.0)
        self.ttretencion = tot_iva_ret.get('s',0.0) - tot_iva_ret.get('r',0.0)
                                

        return ""        

    def _get_tot_gral_compra(self): 
        return self.ttcompra

    def _get_tot_gral_compra_scf(self): 
        return self.ttcompra_sdcf

    def _get_tot_gral_base(self): 
        return self.ttbase 
        
    def _get_tot_gral_iva(self): 
        return self.ttiva

    def _get_tot_gral_retencion(self): 
        return self.ttretencion 

    
      
report_sxw.report_sxw(
    'report.comprobante.retencion',
    'account.retention',
    'addons/retencion_iva/report/comprobante.rml',
    parser=rep_comprobante,
    header=False
)      
