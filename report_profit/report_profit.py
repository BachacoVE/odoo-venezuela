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

from osv import fields,osv
from tools.sql import drop_view_if_exists

class report_profit(osv.osv):
    _name = "report.profit"
    _description = "Profit by Products"
    _auto = False
    _order= "name desc"    
    _columns = {
        'name': fields.date('Month', readonly=True, select=True),
        'product_id':fields.many2one('product.product', 'Product', readonly=True, select=True),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True, select=True),
        'user_id':fields.many2one('res.users', 'User', readonly=True, select=True),
        'quantity': fields.float('# of Products', readonly=True),
        'price_unit': fields.float('Unit Price', readonly=True),
        'last_cost': fields.float('Last Cost', readonly=True),
        'price_subtotal': fields.float('Subtotal Price', readonly=True),
        'last_cost_subtotal': fields.float('Subtotal Last Cost', readonly=True),
        'uom_id': fields.many2one('product.uom', ' UoM', readonly=True),
        'profit': fields.float('Profit', readonly=True),
        'perc': fields.float('Profit Percent', readonly=True),
        'p_uom_c_id':fields.many2one('product.uom.consol', 'Consolidate Unit', readonly=True),
        'qty_consol': fields.float('Consolidate qty', readonly=True),
        'cat_id':fields.many2one('product.category', 'Category', readonly=True),
        'type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
            ],'Type', readonly=True, select=True),
    }

    def init(self, cr):
        drop_view_if_exists(cr, 'report_profit')
        cr.execute("""
            create or replace view report_profit as (
            select
                l.id as id,
                to_char(i.date_invoice, 'YYYY-MM-DD') as name,
                l.product_id as product_id,
                p.id as partner_id,
                u.id as user_id,
                l.quantity as quantity,
                case when i.type='out_refund'
                    then
                        l.price_unit*(-1)
                    else
                        l.price_unit 
                end as price_unit,
                case when i.type='out_refund'
                    then
                        l.last_price*(-1)
                    else
                        l.last_price 
                end as last_cost,                 
                case when i.type='out_refund'
                    then
                        l.price_subtotal*(-1)
                    else
                        l.price_subtotal 
                end as price_subtotal,
                case when i.type='out_refund'
                    then
                        (l.quantity*l.last_price)*(-1)
                    else
                        (l.quantity*l.last_price) 
                end as last_cost_subtotal,
                case when i.type='out_refund'
                    then
                        (price_subtotal-l.quantity*l.last_price)*(-1)
                    else
                        (price_subtotal-l.quantity*l.last_price)
                end as profit,
                case when i.type='out_refund'
                    then
                        ((price_subtotal-l.quantity*l.last_price)*(-1)/(price_subtotal)*100)
                    else
                        ((price_subtotal-l.quantity*l.last_price)/(price_subtotal)*100)
                end as perc,
                l.uos_id as uom_id,
                p.name as partner,
                i.type as type,
                c.p_uom_c_id as p_uom_c_id,
                case when i.type='out_refund'     
                    then                           
                        (l.quantity*c.factor_consol)*(-1)
                    else
                        (l.quantity*c.factor_consol)
                end as qty_consol,
                t.categ_id as cat_id
            from account_invoice i
                inner join res_partner p on (p.id=i.partner_id)
                left join res_users u on (u.id=p.user_id)
                right join account_invoice_line l on (i.id=l.invoice_id)
                left join product_uom m on (m.id=l.uos_id)
                left join product_uom_consol_line c on (m.id=c.p_uom_id)
                left join product_template t on (t.id=l.product_id)
                left join product_product d on (d.product_tmpl_id=l.product_id)
            where l.quantity != 0 and i.type in ('out_invoice', 'out_refund') and i.state in ('open', 'paid') and l.uos_id in (
                select
                    u.id as id
                from product_uom u
                    inner join product_uom_consol_line c on (u.id=c.p_uom_id)
            )
            group by l.id,to_char(i.date_invoice, 'YYYY-MM-DD'),l.product_id,p.id,u.id,l.quantity,l.price_unit,l.last_price,l.price_subtotal,l.uos_id,p.name,i.type,c.p_uom_c_id,c.factor_consol,t.categ_id

            )
        """)
report_profit()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

