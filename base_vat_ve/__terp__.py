# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Netquatro C.A. (http://openerp.netquatro.com/) All Rights Reserved.
#                    Javier Duran <javier.duran@netquatro.com>
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
    'name': 'RIF para Venezuela',
    'version': '0.1',
    'category': 'Generic Modules/Base',
    'description': """
    Habilita y revisa el numero de RIF en Venezuela.
    HABILITA EL CHEQUEO HEREDANDO LA FUNCION DE base_vat ORIGINAL
    DEBE AGREGAR 'VE' ANTES DEL RIF Y LUEGO ESTE CON LAS PROPIEDADES ABAJO DESCRITAS. 
    RIF: JXXXXXXXXX 
    RIF CEDULA VENEZOLANO: VXXXXXXXXX 
    RIF CEDULA EXTRANJERO: EXXXXXXXXX
    QUEDANDO POR EJEMPLO:
    VEJ123456789
    VEV111234456
    VEE112344556
   
    """,
    'author': 'Netquatro',
	"website": "http://openerp.netquatro.com/",
    'depends': ['base', 'account', 'base_vat'],
    'update_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
