# -*- encoding: utf-8 -*-
#############################################################################
#    Module Writen to Odoo 10 Community Edition
#    All Rights Reserved to Experts SA de CV or Experts SAS
#############################################################################
#
#    Coded by: Mauricio Ruiz (mauricio.ruiz@experts.com.mx)
#    Coded by: Daniel Acosta (daniel.acosta@experts.com.mx)
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

    margin_percent = fields.Float(
        string = 'Porcentaje',
        compute = '_get_margin_percent',
        readonly=True,
        default = 0
    )

    def _get_margin_percent(self):
        for record in self:
            if record.margin != 0 and record.amount_untaxed != 0:
                record.margin_percent = record.margin * 100 / record.amount_untaxed

    # Sobre escribimos el método
    
    def action_confirm(self):
        res = super(sale_order, self).action_confirm()
        # Recuperamos la venta
        so_row = self.browse(self._ids)[0]
        # Si la restricción para el margen está puesta
        if so_row.company_id.prevent_sale_margin:
            # Si la restricción es por total de venta
            if so_row.company_id.margin_options == 'sale_total':
                # Obtenemos el monto permitido segun el porcentaje
                allowed = (so_row.amount_untaxed - so_row.margin) * (so_row.company_id.margin_percentage/100)
                if so_row.margin < allowed:
                    raise UserError (_("No tiene permitido este precio en la orden de venta."))
            if so_row.company_id.margin_options == 'sale_line':
                # Para cada linea de venta
                for line in so_row.order_line:
                    allowed = (line.purchase_price * so_row.company_id.margin_percentage/100)
                    if (line.price_subtotal - line.purchase_price) < allowed:
                        raise UserError (_("No tiene permitido este precio de venta en el producto [" + str(line.product_id.default_code) +"] " + str(line.product_id.name)))
        return res

    def action_recompute_margin(self):
        self.ensure_one()
        frm_cur = self.env.user.company_id.currency_id
        to_cur = self.pricelist_id.currency_id
        for line_row in self.order_line:
            purchase_price = line_row.product_id.standard_price
            if line_row.product_uom != line_row.product_id.uom_id:
                purchase_price = line_row.product_id.uom_id._compute_price(purchase_price, line_row.product_uom)
            ctx = self.env.context.copy()
            ctx['date'] = self.date_order
            price = frm_cur.with_context(ctx).compute(purchase_price, to_cur, round=False)
            line_row.purchase_price = price
        for inv_row in self.invoice_ids:
            if inv_row.state in ('open', 'paid') and inv_row.type == 'out_invoice':
                for inv_line_row in inv_row.invoice_line_ids:
                    purchase_price = inv_line_row.product_id.standard_price
                    if inv_line_row.uom_id != inv_line_row.product_id.uom_id:
                        purchase_price = inv_line_row.product_id.uom_id._compute_price(purchase_price, inv_line_row.uom_id)
                    ctx = self.env.context.copy()
                    ctx['date'] = self.date_order
                    price = frm_cur.with_context(ctx).compute(purchase_price, inv_row.currency_id, round=False)
                    inv_line_row.standard_price = price
        return True

    def action_recompute_margin_with_kit(self):
        self.ensure_one()
        frm_cur = self.env.user.company_id.currency_id
        to_cur = self.pricelist_id.currency_id
        for line_row in self.order_line:
            # Si es un kit
            if line_row.product_id.is_kit:
                price = 0
                # Para cada producto del kit en la linea de venta
                for pk in line_row.product_kit_ids:
                    purchase_price = pk.qty * pk.product_name.standard_price
                    ctx = self.env.context.copy()
                    ctx['date'] = self.date_order
                    price += frm_cur.with_context(ctx).compute(purchase_price, to_cur, round=False)
                # Se actualiza el costo
                line_row.purchase_price = price

        for inv_row in self.invoice_ids:
            if inv_row.state in ('open', 'paid') and inv_row.type == 'out_invoice':
                for inv_line_row in inv_row.invoice_line_ids:
                    # Buscamos el producto en las lineas de la SO
                    for sol in self.order_line:
                        if sol.product_id != inv_line_row.product_id:
                            continue
                        else:
                            if inv_line_row.product_id.is_kit:
                                # Le copiamos el costo de la linea de la SO
                                inv_line_row.standard_price = sol.purchase_price
        return True

