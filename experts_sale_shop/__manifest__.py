#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    CopyLeft 2012 - http://experts.com.mx
#    You are free to share, copy, distribute, transmit, adapt and use for commercial purpose
#    More information about license: http://www.gnu.org/licenses/agpl.html
#
#############################################################################
#
#    Coded by: Marco Hernández (marco.hernandez@experts.com.mx)
#
#############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

{
    "name" : 'experts_sale_shop',
    "version" : '0.1',
    "author" : 'experts.com.mx',
    "category" : 'Modules',
    "website" : "",
    "description" : """ Módulo para generar sucursales y sus almacenes. """,
    "init_xml" : [],
    #"depends" : ['base', 'account','account_cancel', 'product', 'stock','sale','sale_stock','experts_groups','experts_account_invoice_cfdi_33'],
    "depends" : ['base', 'account', 'product', 'stock','sale','sale_stock','experts_groups'],
    "data" : [
        'security/ir.model.access.csv',
        'security/groups.xml',
        # 'views/sale_stock_view.xml',
        'views/sale_shop_view.xml',
        'views/sale_order_view.xml',
        'views/product_product_view.xml',
        'views/user_view.xml',
        'views/invoice_view.xml',
        ],
    "demo_xml":[],
    "test":[],
    "installable": True,
    "images": [],
    "auto_install": False,
}
