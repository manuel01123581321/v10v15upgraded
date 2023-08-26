# -*- encoding: utf-8 -*-
#############################################################################
#    Module Writen to Odoo 10 Community Edition
#    All Rights Reserved to Experts SA de CV or Experts SAS
#############################################################################
#
#    Coded by: Mauricio Ruiz(mauricio.ruiz@experts.com.mx)
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

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError

class res_company(models.Model):
    _inherit = 'res.company'

    internal_reference_unique = fields.Boolean(u'Referencia interna única')
    show_barcode_in_tree_view = fields.Boolean(u'Mostrar el código de barras en la vista lista de productos')


    def write(self, vals):
        res = super(res_company, self).write(vals)
        # Assign all users groups fot hide/show in product tree
        group_view_showbarcode = self.env.ref('experts_product_extend.group_view_showbarcode', False)
        group_hide_fields = self.env.ref('experts_product_extend.group_view_hidden_fields', False)
        users = self.env['res.users'].search([])
        print users
        if 'show_barcode_in_tree_view' in vals:
            if vals.get("show_barcode_in_tree_view",False):
                for user in users:
                    group_view_showbarcode.write({'users': [(4, user.id)]})
                    group_hide_fields.write({'users': [(3, user.id)]})
            else:
                for user in users:
                    group_hide_fields.write({'users': [(4, user.id)]})
                    group_view_showbarcode.write({'users': [(3, user.id)]})

        return res
        