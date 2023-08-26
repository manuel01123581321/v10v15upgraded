#!/usr/bin/env python
# -*- encoding: utf-8 -*- 
#############################################################################
#    Module Writen to Odoo 10 Community Edition
#    All Rights Reserved to Experts SA de CV or Experts SAS
#############################################################################
#
#    Coded by: Carlos Blanco (carlos.blanco@experts.com.mx)
#    Migrated by: Carlos Blanco (carlos.blanco@experts.com.mx)
#
#############################################################################
#    This software and associated files (the "Software") can only be used
#    (executed, modified, executed after modifications) with a valid purchase
#    of these module with Experts SA de CV or Experts SAS.
#
#    You may develop Odoo modules that use this Software as a library
#    (typically by depending on it, importing it and using its resources),
#    but without copying any source code or material from the Software.
#
#    You may distribute those modules under the license of your choice,
#    provided that this license is compatible with the terms of this license.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies of
#    the Software or modified copies of the Software.
#
#    The above copyright notice and this permission notice must be included in
#    all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#    THE SOFTWARE.
#############################################################################

from odoo import api, fields, models, _ ,SUPERUSER_ID

class ResUsers(models.Model):
    _inherit='res.users'

    shop_id = fields.Many2one('sale.shop', string="Sucursal por defecto")
    shop_ids = fields.Many2many('sale.shop','shop_user_rel','user_id','shop_id','Sucursales permitidas')

    
    @api.onchange('shop_ids')
    def onchange_shop_id(self):
        for record in self:
            res={}
            if not self.env['res.users']._fields.get('warehouse_ids', False):
                return {}
            ids_warehouse=[]
            for warehouse_row in record.warehouse_ids:
                ids_warehouse.append(warehouse_row.id)
            for shop_row in record.shop_ids:
                for shop_warehouse_row in shop_row.ware_house_ids:
                    if shop_warehouse_row.warehouse_id.id not in ids_warehouse:
                        ids_warehouse.append(shop_warehouse_row.warehouse_id.id)
            record.warehouse_ids = ids_warehouse
            return res

class Company(models.Model):
    _inherit = 'res.company'

    prevent_product_exists_warning = fields.Boolean('Eliminar advertencia en ventas con producto sin existencias', default=False)
