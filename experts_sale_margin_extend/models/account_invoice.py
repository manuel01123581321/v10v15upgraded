# -*- encoding: utf-8 -*-
#############################################################################
#    Module Writen to Odoo 10 Community Edition
#    All Rights Reserved to Experts SA de CV or Experts SAS
#############################################################################
#
#    Coded by: Marco Hernández (marco.hernandez@experts.com.mx)
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

from odoo import api, fields, models, _, SUPERUSER_ID
import odoo.addons.decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = "account.move"
    #los campos computados deben tener store=True
    margin_percent = fields.Float(
        string='Porcentaje',
        compute='_get_margin_percent',
        store=True,
        default=0
    )

    def _get_margin_percent(self):
        for record in self:
            if not record.move_type == 'in_invoice': #solo para facturas cliente, no aplica para proveedor
                if record.margin_in_invoice != 0 and record.amount_untaxed != 0:
                    record.margin_percent = record.margin_in_invoice * 100 / record.amount_untaxed

    def _get_cost_total(self):
        for invoice_row in self:
            cost_total = 0
            for line in invoice_row.invoice_line_ids:
                cost_line = 0
                cost_line = line.standard_price * line.quantity
                cost_total += cost_line
            invoice_row.cost_in_invoice = cost_total
        return {}

    def _get_margin(self):
        for invoice_row in self:
            if invoice_row.move_type == 'out_invoice': #solo para facturas cliente, no aplica para proveedor
                print('entro a _get_margin')
                margin = 0
                margin = sum(line.margin_line for line in invoice_row.invoice_line_ids)
                invoice_row.margin_in_invoice = margin
        return {}

    cost_in_invoice = fields.Float('Costo Total', compute="_get_cost_total", store=False)
    margin_in_invoice = fields.Float('Margen', compute="_get_margin", store=True)

    def action_invoice_open(self):
        for invoice_row in self:
            for line_row in invoice_row.invoice_line_ids:
                line_row.product_id_change_margin()
        return super(AccountInvoice, self).action_invoice_open()

    def recompute_margin_invoice(self):
        for inv_row in self:
            for line_row in inv_row.invoice_line_ids:
                line_row.product_id_change_margin()
        return True


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    # standard_price = fields.Float(string='Costo de producto')
    # margin_line = fields.Float(string='Margen de producto')

    margin_line = fields.Float(string='Margen de producto', compute='_product_margin',
                               digits=dp.get_precision('Product Price'), store=True)
    standard_price = fields.Float(string='Costo de producto', digits=dp.get_precision('Product Price'))

    def get_cost_kit(self, product_id):
        # El costo del kit se obtiene de la SO dado que es ahi donde especifican/modifican cantidades
        for line in self:
            # Revisamos si el origen es una venta
            sale_id = self.env['sale.order'].search([('name', '=', line.move_id.origin)])
            cost = 0
            # Para cada linea de la SO
            for sol in sale_id.order_line:
                # Si el producto de la factura corresponde con el poructo de la linea de la SO
                if product_id == sol.product_id:
                    # Obtenemos el costo del kit según la SO
                    cost = 0
                    for pk in sol.product_kit_ids:
                        cost += pk.qty * pk.product_name.standard_price
            # ~ for product_kit in product_id.product_kit_ids:
            # ~ cost += product_kit.product_name.standard_price * product_kit.qty
            return cost

    def _compute_margin(self, invoice_id, product_id, uom_id):
        if self.move_id.move_type == 'out_invoice':
            frm_cur = self.env.user.company_id.currency_id
            to_cur = invoice_id.currency_id
            if product_id._fields.get('is_kit', False):
                if product_id.is_kit:
                    purchase_price = self.get_cost_kit(product_id)
                else:
                    purchase_price = product_id.standard_price
            else:
                purchase_price = product_id.standard_price
            if uom_id != product_id.uom_id:
                purchase_price = product_id.uom_id._compute_price(purchase_price, uom_id)
            ctx = self.env.context.copy()
            price = frm_cur.with_context(ctx).compute(purchase_price, to_cur, round=False)
            return price

    @api.onchange('product_id', 'uom_id')
    def product_id_change_margin(self):
        if not self.move_id.move_type == 'in_invoice':
            if not self.product_id or not self.product_uom_id:
                return
            self.standard_price = self._compute_margin(self.move_id, self.product_id, self.product_uom_id)

    @api.depends('product_id', 'standard_price', 'quantity', 'price_unit', 'price_subtotal')
    def _product_margin(self):
        for line in self:
            currency = line.move_id.currency_id
            price = line.standard_price
            if not price:
                from_cur = self.env.user.company_id.currency_id
                if line.product_id._fields.get('is_kit', False):
                    if line.product_id.is_kit:
                        purchase_price = self.get_cost_kit(line.product_id)
                    else:
                        purchase_price = line.product_id.standard_price
                else:
                    purchase_price = line.product_id.standard_price
                if line.product_id and line.product_uom_id != line.product_id.uom_id:
                    purchase_price = line.product_id.uom_id._compute_price(purchase_price, line.product_uom_id)
                price = from_cur.compute(purchase_price, currency, round=False)
                line.standard_price = price
            line.margin_line = currency.round(line.price_subtotal - (price * line.quantity))
