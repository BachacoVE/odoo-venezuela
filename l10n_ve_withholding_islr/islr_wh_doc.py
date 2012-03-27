#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <hbto@vauxoo.com>
#              Maria Gabriela Quilarque  <gabriela@vauxoo.com>
#              Javier Duran              <javier@vauxoo.com>
#    Planified by: Nhomar Hernandez <nhomar@vauxoo.com>
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha hbto@vauxoo.com
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################
from osv import osv
from osv import fields
from tools.translate import _
from tools import config
import time
import datetime
import decimal_precision as dp

class islr_wh_doc(osv.osv):

    def _get_type(self, cr, uid, context=None):
        if context is None:
            context = {}
        type = context.get('type', 'in_invoice')
        return type

    def _get_journal(self, cr, uid, context):
        if context is None:
            context = {}
        type_inv = context.get('type')
        type2journal = {'out_invoice': 'retislrSale', 'in_invoice': 'retislrPurchase', 'out_refund': 'retislrSale', 'in_refund': 'retislrPurchase'}
        journal_obj = self.pool.get('account.journal')
        res = journal_obj.search(cr, uid, [('type', '=', type2journal.get(type_inv, 'retislrPurchase'))], limit=1)
        if res:
            return res[0]
        else:
            return False

    def _get_currency(self, cr, uid, context):
        user = self.pool.get('res.users').browse(cr, uid, [uid])[0]
        if user.company_id:
            return user.company_id.currency_id.id
        else:
            return self.pool.get('res.currency').search(cr, uid, [('rate','=',1.0)])[0]

    def _get_amount_total(self,cr,uid,ids,name,args,context=None):
        res = {}
        for rete in self.browse(cr,uid,ids,context):
            res[rete.id]= 0.0
            for line in rete.concept_ids:
                res[rete.id] += line.amount
        return res

    def _get_period(self,cr,uid,ids,name,args,context={}):
        res = {}
        wh_doc_brw = self.browse(cr,uid,ids, context=None)
        for doc in wh_doc_brw:
            if doc.date_ret:
                period_ids = self.pool.get('account.period').search(cr,uid,[('date_start','<=',doc.date_ret or time.strftime('%Y-%m-%d')),('date_stop','>=',doc.date_ret or time.strftime('%Y-%m-%d'))])
                if len(period_ids):
                    period_id = period_ids[0]
                res[doc.id] = period_id
        return res

    def filter_lines_invoice(self,cr,uid,partner_id,context):
        inv_obj = self.pool.get('account.invoice')
        invoice_obj = self.pool.get('islr.wh.doc.invoices')
        inv_ids=[]
        
        inv_ids = inv_obj.search(cr,uid,[('state', '=', 'open'),('partner_id','=',partner_id)],context={})
        if inv_ids:
            #~ Get only the invoices which are not in a document yet
            inv_ids = [i.id for i in inv_obj.browse(cr,uid,inv_ids,context={})  if not i.islr_wh_doc_id]
            inv_ids = [i for i in inv_ids if not invoice_obj.search(cr, uid, [('invoice_id', '=', i)])]
            inv_ids = [i.id for i in inv_obj.browse(cr, uid, inv_ids, context={}) for d in i.invoice_line if d.concept_id.withholdable]
        return inv_ids
    
    _name = "islr.wh.doc"
    _description = 'Document Withholding Income'
    _columns= {
        'name': fields.char('Description', size=64,readonly=True, states={'draft':[('readonly',False)]}, required=True, help="Voucher description"),
        'code': fields.char('Code', size=32, readonly=True, states={'draft':[('readonly',False)]}, help="Voucher reference"),
        'number': fields.char('Withhold Number', size=32, readonly=True, states={'draft':[('readonly',False)]}, help="Voucher reference"),
        'type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('in_refund','Supplier Invoice Refund'),
            ('out_refund','Customer Invoice Refund'),
            ],'Type', readonly=True, help="Voucher type"),
        'state': fields.selection([
            ('to_process','To Process'),
            ('progress','Progress'),
            ('draft','Draft'),
            ('confirmed', 'Confirmed'),
            ('done','Done'),
            ('cancel','Cancelled')
            ],'State', readonly=True, help="Voucher state"),
        'date_ret': fields.date('Accounting Date', help="Keep empty to use the current date"),
        'date_uid': fields.date('Withhold Date', readonly=True, help="Voucher date"),
        'period_id': fields.function(_get_period, method=True, required=False, type='many2one',relation='account.period', string='Period', help="Period when the accounts entries were done"),
        'account_id': fields.many2one('account.account', 'Account', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="Account Receivable or Account Payable of partner"),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True, required=True, states={'draft':[('readonly',False)]}, help="Partner object of withholding"),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="Currency in which the transaction takes place"),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True,readonly=True, states={'draft':[('readonly',False)]}, help="Journal where accounting entries are recorded"),
        'company_id': fields.many2one('res.company', 'Company', required=True, help="Company"),
        'amount_total_ret':fields.function(_get_amount_total,method=True, string='Amount Total', type='float', digits_compute= dp.get_precision('Withhold ISLR'),  help="Total Withheld amount"),
        'concept_ids': fields.one2many('islr.wh.doc.line','islr_wh_doc_id','Withholding Income Concept', readonly=True, states={'draft':[('readonly',False)]}),
        'invoice_ids':fields.one2many('islr.wh.doc.invoices','islr_wh_doc_id','Withheld Invoices'),
        'invoice_id':fields.many2one('account.invoice','Invoice',readonly=False,help="Invoice to make the accounting entry"),
        'islr_wh_doc_id': fields.one2many('account.invoice','islr_wh_doc_id','Invoices',states={'draft':[('readonly',False)]}),
        'user_id': fields.many2one('res.users', 'Salesman', readonly=True, states={'draft':[('readonly',False)]}),
    }

    _defaults = {
        'code': lambda obj, cr, uid, context: obj.pool.get('islr.wh.doc').retencion_seq_get(cr, uid, context),
        'type': _get_type,
        'state': 'draft',
        'journal_id': _get_journal,
        'currency_id': _get_currency,
        'company_id': lambda self, cr, uid, context: \
                self.pool.get('res.users').browse(cr, uid, uid,
                    context=context).company_id.id,
        'user_id': lambda s, cr, u, c: u,
    }

    def validate(self, cr,uid,ids,*args):

        if args[0]in ['in_invoice','in_refund'] and args[1] and args[2]:
            return True

    def action_process(self,cr,uid,ids, *args):
        inv_obj=self.pool.get('account.invoice')
        context = {}
        wh_doc_brw = self.browse(cr, uid, ids, context=None)
        inv_ids = []
        
        for wh_doc in wh_doc_brw:
            for wh_doc_line in wh_doc.islr_wh_doc_id: 
                inv_ids.append(wh_doc_line.id)
        context["wh_doc_id"]=ids[0]
        inv_obj.action_ret_islr(cr, uid, inv_ids,context)
        return True

    def action_cancel_process(self,cr,uid,ids,context=None):
        if not context:
            context={}
        line_obj = self.pool.get('islr.wh.doc.line')
        doc_inv_obj = self.pool.get('islr.wh.doc.invoices')
        inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')
        
        wh_doc_id = ids[0]
        #~ wh_line_list = line_obj.search(cr,uid,[('islr_wh_doc_id','=',wh_doc_id)])
        #~ line_obj.unlink(cr,uid,wh_line_list)
        
        #~ doc_inv_list = doc_inv_obj.search(cr,uid,[('islr_wh_doc_id','=',wh_doc_id)])
        #~ doc_inv_obj.unlink(cr,uid,doc_inv_list)
        
        inv_list = inv_obj.search(cr,uid,[('islr_wh_doc_id','=',wh_doc_id)])
        inv_obj.write(cr, uid, inv_list, {'status':'no_pro','islr_wh_doc_id':None})
        
        inv_line_list = inv_line_obj.search(cr,uid,[('invoice_id','in',inv_list)])
        inv_line_obj.write(cr, uid, inv_line_list, {'apply_wh':False})
        
        return True

    def retencion_seq_get(self, cr, uid, context=None):
        pool_seq=self.pool.get('ir.sequence')
        cr.execute("select id,number_next,number_increment,prefix,suffix,padding from ir_sequence where code='islr.wh.doc' and active=True")
        res = cr.dictfetchone()
        if res:
            if res['number_next']:
                return pool_seq._process(res['prefix']) + '%%0%sd' % res['padding'] % res['number_next'] + pool_seq._process(res['suffix'])
            else:
                return pool_seq._process(res['prefix']) + pool_seq._process(res['suffix'])
        return False

    def onchange_partner_id(self, cr, uid, ids, type, partner_id):
        acc_id = False
        inv_ids=[]

        if partner_id:
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if type in ('out_invoice', 'out_refund'):
                acc_id = p.property_account_receivable.id
                inv_ids = self.filter_lines_invoice(cr,uid,partner_id,context=None)
            else:
                acc_id = p.property_account_payable.id
        result = {'value': {'islr_wh_doc_id':inv_ids,'account_id': acc_id}}

        return result

    def create(self, cr, uid, vals, context=None, check=True):
        if not context:
            context={}
        code = self.pool.get('ir.sequence').get(cr, uid, 'islr.wh.doc')
        vals['code'] = code
        return super(islr_wh_doc, self).create(cr, uid, vals, context)

    def action_confirm1(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'confirmed'})


    def action_number(self, cr, uid, ids, *args):
        obj_ret = self.browse(cr, uid, ids)[0]
        cr.execute('SELECT id, number ' \
                'FROM islr_wh_doc ' \
                'WHERE id IN ('+','.join(map(str,ids))+')')

        for (id, number) in cr.fetchall():
            if not number:
                number = self.pool.get('ir.sequence').get(cr, uid, 'islr.wh.doc.%s' % obj_ret.type)
            cr.execute('UPDATE islr_wh_doc SET number=%s ' \
                    'WHERE id=%s', (number, id))
        return True

    def action_done1(self, cr, uid, ids, context={}):
        self.action_number(cr, uid, ids)
        self.action_move_create(cr, uid, ids)
        self.write(cr, uid, ids, {'state':'done'})
        return True

    def action_cancel(self,cr,uid,ids,context={}):
        if self.browse(cr,uid,ids)[0].type=='in_invoice':
            return True
        self.cancel_move(cr,uid,ids)
        self.action_cancel_process(cr,uid,ids,context=context)
        return True
        
    


    def cancel_move (self,cr,uid,ids, *args):
        context={}
        ret_brw = self.browse(cr, uid, ids)
        account_move_obj = self.pool.get('account.move')
        for ret in ret_brw:
            if ret.state == 'done':
                for ret_line in ret.concept_ids:
                    account_move_obj.button_cancel(cr, uid, [ret_line.move_id.id])
                    delete = account_move_obj.unlink(cr, uid,[ret_line.move_id.id])
                if delete:
                    self.write(cr, uid, ids, {'state':'cancel'})
            else:
                self.write(cr, uid, ids, {'state':'cancel'})
        return True


    def action_cancel_draft(self,cr,uid,ids, *args):
        self.write(cr, uid, ids, {'state':'draft'})
        return True

    def action_move_create(self, cr, uid, ids, *args):

        wh_doc_obj = self.pool.get('islr.wh.doc.line')
        context = {}
        inv_id = None
        doc_brw = None
        
        for ret in self.browse(cr, uid, ids):
            if not ret.date_uid:
                self.write(cr, uid, [ret.id], {'date_uid':time.strftime('%Y-%m-%d')})

            if not ret.date_ret:
                self.write(cr, uid, [ret.id], {'date_ret':time.strftime('%Y-%m-%d')})
            
            period_id = ret.period_id and ret.period_id.id or False
            journal_id = ret.journal_id.id
            
            if not period_id:
                period_ids = self.pool.get('account.period').search(cr,uid,[('date_start','<=',ret.date_ret or time.strftime('%Y-%m-%d')),('date_stop','>=',ret.date_ret or time.strftime('%Y-%m-%d'))])
                if len(period_ids):
                    period_id = period_ids[0]
                else:
                    raise osv.except_osv(_('Warning !'), _("Not found a fiscal period to date: '%s' please check!") % (ret.date_ret or time.strftime('%Y-%m-%d')))

            if ret.concept_ids:
                for line in ret.concept_ids:
                    if ret.type in ('in_invoice', 'in_refund'):
                        if line.concept_id.property_retencion_islr_payable:
                            acc_id = line.concept_id.property_retencion_islr_payable.id
                            inv_id = ret.invoice_id.id
                        else:
                            raise osv.except_osv(_('Invalid action !'),_("Impossible withholding income, because the account for withholding of sale is not assigned to the Concept withholding '%s'!")% (line.concept_id.name))
                    else:
                        if  line.concept_id.property_retencion_islr_receivable:
                            acc_id = line.concept_id.property_retencion_islr_receivable.id
                            inv_id = line.invoice_id.id
                        else:
                            raise osv.except_osv(_('Invalid action !'),_("Impossible withholding income, because the account for withholding of purchase is not assigned to the Concept withholding '%s'!") % (line.concept_id.name))

                    writeoff_account_id = False
                    writeoff_journal_id = False
                    amount = line.amount

                    ret_move = self.wh_and_reconcile(cr, uid, [ret.id], inv_id,
                            amount, acc_id, period_id, journal_id, writeoff_account_id,
                            period_id, writeoff_journal_id, context)

                    # make the retencion line point to that move
                    rl = {
                        'move_id': ret_move['move_id'],
                    }
                    #lines = [(op,id,values)] escribir en un one2many
                    lines = [(1, line.id, rl)]
                    self.write(cr, uid, [ret.id], {'concept_ids':lines})
                  
                    if lines:
                        message = _("Withholding income voucher '%s' validated and accounting entry generated.") % self.browse(cr, uid, ids[0]).name
                        self.log(cr, uid, ids[0], message) 
                  
                    for line in ret.concept_ids:
                        for xml in line.xml_ids:
                            if xml.islr_xml_wh_doc.state!='done':
                                if xml.period_id.id != period_id:
                                    self.pool.get('islr.xml.wh.line').write(cr,uid,xml.id,{'period_id':period_id, 'islr_xml_wh_doc':None})
                            else:
                                raise osv.except_osv(_('Invalid action !'),_("Impossible change the period accountig to a withholding that has already been declared."))
#                    inv_obj.write(cr, uid, line.invoice_id.id, {'retention':True}, context=context)
        return True


    def wh_and_reconcile(self, cr, uid, ids, invoice_id, pay_amount, pay_account_id, period_id, pay_journal_id, writeoff_acc_id, writeoff_period_id, writeoff_journal_id,context=None, name=''):
        
        inv_obj = self.pool.get('account.invoice')
        ret = self.browse(cr, uid, ids)[0]
        if context is None:
            context = {}
        #TODO check if we can use different period for payment and the writeoff line
        #~ assert len(invoice_ids)==1, "Can only pay one invoice at a time"
        invoice = inv_obj.browse(cr, uid, invoice_id)
        src_account_id = invoice.account_id.id
        # Take the seq as name for move
        types = {'out_invoice': -1, 'in_invoice': 1, 'out_refund': 1, 'in_refund': -1}
        direction = types[invoice.type]
       
        date=ret.date_ret
            
        l1 = {
            'debit': direction * pay_amount>0 and direction * pay_amount,
            'credit': direction * pay_amount<0 and - direction * pay_amount,
            'account_id': src_account_id,
            'partner_id': invoice.partner_id.id,
            'ref':invoice.number,
            'date': date,
            'currency_id': False,
        }
        l2 = {
            'debit': direction * pay_amount<0 and - direction * pay_amount,
            'credit': direction * pay_amount>0 and direction * pay_amount,
            'account_id': pay_account_id,
            'partner_id': invoice.partner_id.id,
            'ref':invoice.number,
            'date': date,
            'currency_id': False, 
        }
        if not name:
            if invoice.type in ['in_invoice','in_refund']:
                name = 'COMP. RET. ISLR ' + ret.number + ' Doc. '+ (invoice.reference or '')
            else:
                name = 'COMP. RET. ISLR ' + ret.number + ' Doc. '+ (invoice.number or '')

        l1['name'] = name
        l2['name'] = name

        lines = [(0, 0, l1), (0, 0, l2)]
        move = {'ref': invoice.number, 'line_id': lines, 'journal_id': pay_journal_id, 'period_id': period_id, 'date': date}
        move_id = self.pool.get('account.move').create(cr, uid, move, context=context)

        self.pool.get('account.move').post(cr, uid, [move_id])

        line_ids = []
        total = 0.0
        line = self.pool.get('account.move.line')
        cr.execute('select id from account_move_line where move_id in ('+str(move_id)+','+str(invoice.move_id.id)+')')
        lines = line.browse(cr, uid, map(lambda x: x[0], cr.fetchall()) )
        for l in lines+invoice.payment_ids:
            if l.account_id.id==src_account_id:
                line_ids.append(l.id)
                total += (l.debit or 0.0) - (l.credit or 0.0)
        if (not round(total,self.pool.get('decimal.precision').precision_get(cr, uid, 'Withhold ISLR'))) or writeoff_acc_id:
            self.pool.get('account.move.line').reconcile(cr, uid, line_ids, 'manual', writeoff_acc_id, writeoff_period_id, writeoff_journal_id, context)
        else:
            self.pool.get('account.move.line').reconcile_partial(cr, uid, line_ids, 'manual', context)

        # Update the stored value (fields.function), so we write to trigger recompute
        self.pool.get('account.invoice').write(cr, uid, invoice_id, {}, context=context)
        return {'move_id': move_id}


    def action_ret_islr(self, cr, uid, ids, context={}):
        #TODO: :
        inv_obj = self.pool.get('account.invoice')
        invoices_brw = inv_obj.browse(cr, uid, ids, context)
        wh_doc_list = []
        for invoice in invoices_brw:
            wh_doc_list = inv_obj.pool.get('islr.wh.doc.invoices').search(cr,uid,[('invoice_id','=',invoice.id)])  
            if wh_doc_list: #Chequear que la factura no haya sido retenida.
                raise osv.except_osv(_('Invalid action !'),_("The Withholding invoice '%s' has already been done!") % (invoice.number))
            else: # 1.- Si la factura no ha sido retenida
                wh_dict={}
                dict_rate={}
                dict_completo={}
                vendor, buyer, apply_wh = inv_obj._get_partners(cr,uid,invoice) # Se obtiene el (vendedor, el comprador, si el comprador es agente de retencion)
                concept_list = inv_obj._get_concepts(cr,uid,invoice)# Se obtiene la lista de conceptos de las lineas de la factura actual.
                if concept_list:  # 2.- Si existe algun concepto de retencion en las lineas de la factura.
                    if apply_wh:  # 3.- Si el comprador es agente de retencion
                        wh_dict = inv_obj._get_service_wh(cr, uid, invoice, concept_list) # Se obtiene un dic con la lista de lineas de factura, si se aplico retencion alguna vez, el monto base total de las lineas.
                        residence = inv_obj._get_residence(cr, uid, vendor, buyer) # Retorna el tipo de residencia del vendedor
                        nature = inv_obj._get_nature(cr, uid, vendor) # Retorna la naturaleza del vendedor.
                        dict_rate = inv_obj._get_rate_dict(cr, uid, concept_list, residence, nature,context) # Retorna las tasas por cada concepto
                        inv_obj._pop_dict(cr,uid,concept_list,dict_rate,wh_dict) # Borra los conceptos y las lineas de factura que no tengan tasa asociada.
                        dict_completo = inv_obj._get_wh_apply(cr,uid,dict_rate,wh_dict,nature) # Retorna el dict con todos los datos de la retencion por linea de factura.
                        islr_wh_doc_id=inv_obj._logic_create(cr,uid,dict_completo,context.get('wh_doc_id',False))# Se escribe y crea en todos los modelos asociados al islr.
                    else:
                        raise osv.except_osv(_('Invalid action !'),_("Impossible withholding income, because the supplier '%s' withholding agent is not!") % (buyer.name))
                else:
                    raise osv.except_osv(_('Invalid action !'),_("Impossible withholding income, because the lines of the invoice has not concept withholding!"))
            break
        return islr_wh_doc_id


islr_wh_doc()


class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
        'islr_wh_doc_id': fields.many2one('islr.wh.doc','Withhold Document',readonly=True,help="Document Retention income tax generated from this bill"),
    }
    _defaults = {
        'islr_wh_doc_id': lambda *a: 0,
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'islr_wh_doc_id':0 })

        return super(account_invoice, self).copy(cr, uid, id, default, context)
        
account_invoice()
        
        
class islr_wh_doc_invoices(osv.osv):
    _name = "islr.wh.doc.invoices"
    _description = 'Document and Invoice Withheld Income'
    _columns= {
        'islr_wh_doc_id': fields.many2one('islr.wh.doc','Withhold Document', ondelete='cascade', help="Document Retention income tax generated from this bill"),
        'invoice_id':fields.many2one('account.invoice','Invoice', help="Withheld invoice"),
    }
    _rec_rame = 'invoice_id'
islr_wh_doc_invoices()


class islr_wh_doc_line(osv.osv):
    _name = "islr.wh.doc.line"
    _description = 'Lines of Document Withholding Income'

    def _retention_rate(self, cr, uid, ids, name, args, context=None):
        res = {}
        for ret_line in self.browse(cr, uid, ids, context=context):
            if ret_line.invoice_id:
                pass
            else:
                res[ret_line.id] = 0.0
        return res

    _columns= {
        'name': fields.char('Description', size=64, help="Description of the voucher line"),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', ondelete='set null', help="Invoice to withhold"),
        'amount':fields.float('Amount', digits_compute= dp.get_precision('Withhold ISLR'), help="Withheld amount"),
        'islr_wh_doc_id': fields.many2one('islr.wh.doc','Withhold Document', ondelete='cascade', help="Document Retention income tax generated from this bill"),
        'concept_id': fields.many2one('islr.wh.concept','Withhold  Concept', help="Withhold concept associated with this rate"),
        'retencion_islr':fields.float('Percentage', digits_compute= dp.get_precision('Withhold ISLR'), help="Withholding percentage"),
        'retention_rate': fields.function(_retention_rate, method=True, string='Withholding Rate', type='float', help="Withhold rate has been applied to the invoice", digits_compute= dp.get_precision('Withhold ISLR')),
        'move_id': fields.many2one('account.move', 'Journal Entry', readonly=True, help="Accounting voucher"),
        'islr_rates_id': fields.many2one('islr.rates','Rates', help="Withhold rates"),
        'xml_ids':fields.one2many('islr.xml.wh.line','islr_wh_doc_line_id','XML Lines'),        
    }

islr_wh_doc_line()






