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

class StockPicking(models.Model):
    _inherit = "stock.picking"


    def get_so_notes(self):
        for row in self:
            # Buscamos la SO asociada
            if row.origin:
                so_id = self.env['sale.order'].search([('name','=',row.origin)])
                if so_id:
                    row.so_notes = so_id.note
            else:
                row.so_notes = ""
        return {}

    so_notes = fields.Text("Notas de la orden de venta", readonly=True, compute="get_so_notes")
    picking_notes = fields.Text(string='Notas para almacén', readonly=True)

    @api.model
    def create(self, vals):
        pick_row = super(StockPicking, self).create(vals)
        if pick_row.picking_type_id.code == 'outgoing':
            # Get sale order to asign notes
            sale_row = self.env['sale.order'].search([('name','=',pick_row.origin)])
            if sale_row:
                pick_row.picking_notes = sale_row.picking_notes
        return pick_row

class StockMove(models.Model):
    _inherit = "stock.move"

    notes_line = fields.Text(string='Notas', readonly=True)

    @api.model
    def create(self, vals):
        # If procurement exists, asign notes for each line
        if vals.has_key('procurement_id'):
            procurement_row = self.env['procurement.order'].search([('id','=',vals['procurement_id'])])
            if procurement_row:
                sale_line_row = self.env['sale.order.line'].search([('id','=',procurement_row.sale_line_id.id)])
                # Assign notes for each line in picking
                vals['notes_line'] = sale_line_row.notes_line
        res = super(StockMove, self).create(vals)
        return res
