# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Netquatro C.A. (http://openerp.netquatro.com/) All Rights Reserved.
#                    Javier Duran <javier.duran@netquatro.com>
#                    Nhomar Hernandéz <nhomar.hernandez@netquatro.com>
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

{
    "name" : "Fiscal Report For Venezuela",
    "version" : "0.2",
    "depends" : ["account","retencion_iva",],
    "author" : "Netquatro",
    "description" : """
    What this module does:
    Build all Fiscal Reports for Law in Venezuela.
    -- Purchase Report.
    -- Sales Report.
    -- Withholding Report.
        Sales, Purchase, ISLR and Munic.
    """,
    "website" : "http://openerp.netquatro.com",
    "category" : "Generic Modules/Accounting",
    "init_xml" : [
    ],
    "demo_xml" : [
    ],
    "update_xml" : [
        "security/ir.model.access.csv",    
        "fiscal_report_purchase_view.xml",
        "fiscal_report_sale_view.xml",
        "fiscal_report_whp.xml",
        "fiscal_report_whs.xml",
        "fiscal_report_report.xml",
        "fiscal_report_wizard.xml",
    ],
    "active": False,
    "installable": True,
}
