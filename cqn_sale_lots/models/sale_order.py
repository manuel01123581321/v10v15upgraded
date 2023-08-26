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
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class sale_order(models.Model):
    _inherit = 'sale.order'

    picking_notes = fields.Text(string='Notas para almacén', states={'sale': [('readonly', True)],
        'cancel': [('readonly', True)], 'done': [('readonly', True)]},)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    notes_line = fields.Text(string='Notas', states={'sale': [('readonly', True)], 'cancel': [('readonly', True)],
        'done': [('readonly', True)]},)

    def get_lots(self):
        # Se crea el wizard
        wizard_id = self.env['sale.order.lots.wizard'].create({'product_id': self.product_id.id})
        # Filtramos los lotes con el producto en cuestión
        lots_ids = self.env['stock.production.lot'].search([('product_id','=',self.product_id.id)])
        lots_list = []
        qty = 0
        qty_reserved = 0
        qty_available = 0
        # Para cada lote
        for lot in lots_ids:
            # Para cada quant
            for quant in lot.quant_ids:
                # Si el quant tiene almacén
                if quant.warehouse_id:
                    vals = {
                        'lot_id': lot.id,
                        'qty': quant.qty,
                        'expiry_date': lot.removal_date,
                        'location_id': quant.warehouse_id.lot_stock_id.id,
                        'wizard_id': wizard_id.id,
                    }
                    lots_list.append((0,0,vals))
        # Obtenemos la cantidad disponible del producto
        qty_available = wizard_id.product_id.qty_available
        # Obtenemos la cantidad reservada del producto (aún no se sabe a que lote pertenece)
        qty_reserved = wizard_id.product_id.outgoing_qty
        # Actualizamos el wizard
        wizard_id.write({'lots_ids': lots_list, 'qty_reserved':qty_reserved,'qty_available':qty_available})
        # Se devuelve el wizard
        return {
            'name': u'Lotes de producto',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.lots.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': wizard_id.id,
            'target': 'new',
        }
