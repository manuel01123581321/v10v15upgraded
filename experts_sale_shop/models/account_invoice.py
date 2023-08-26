#!/usr/bin/env python
# -*- encoding: utf-8 -*- 
#############################################################################
#    Module Writen to Odoo 10 Community Edition
#    All Rights Reserved to Experts SA de CV or Experts SAS
#############################################################################
#
#    Coded by: Mauricio Ruiz (mauricio.ruiz@experts.com.mx)
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

class AccountInvoice(models.Model):
    _inherit = 'account.move'
        
    def _get_list(self):
        shops = []
        # Obtenemos las tiendas  a las que pertenece el usuario
        if self.env.user.shop_ids:
            for shop in self.env.user.shop_ids:
                shops.append(shop.id)
        return shops

    def _get_default_shop_2(self):
        if self.env.user.shop_id:
            return self.env.user.shop_id.id
        return False

    def _get_shops(self):
        shops = self._get_list()
        return "[('id','in',[" + ','.join(map(str, list(shops))) + "])]"

    shop_id = fields.Many2one('sale.shop', string="Tienda", required=True, domain=_get_shops,readonly=True, states={'draft': [('readonly', False)]}, default=_get_default_shop_2)


    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        values = super(AccountInvoice, self)._prepare_refund(invoice,date_invoice,date,description,journal_id)
        if invoice.shop_id:
            values.update({'shop_id': invoice.shop_id.id})
        return values









