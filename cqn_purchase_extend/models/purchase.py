# -*- encoding: utf-8 -*- 
#############################################################################
#    Module Writen to Odoo 10 Community Edition
#    All Rights Reserved to Experts SA de CV or Experts SAS
#############################################################################
#
#    Coded by: Marco Hernández (marco.hernandez@experts.com.mx)
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
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    user_confirm_id = fields.Many2one('res.users', 'Usuario que confirma', readonly=True)

    def button_confirm(self):
        res = super(PurchaseOrder,self).button_confirm()
        self.write({'user_confirm_id': self.env.user.id})
        return res

   
class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _get_cost_by_shop(self):
        for line in self:
            cost_shop = ''
            for cost in line.product_id.supplier_cost_ids:
                cost_shop += '** ' + cost.shop_id.name + ' - ' + str('{:.2f}'.format(cost.supplier_cost)) + ', '
            line.cost_by_shop = cost_shop
        return True

    cost_by_shop = fields.Char(string='Costo Tienda', compute='_get_cost_by_shop',  store=False)