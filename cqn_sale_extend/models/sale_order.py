# -*- encoding: utf-8 -*-
#############################################################################
#    Module Writen to Odoo 10 Community Edition
#    All Rights Reserved to Experts SA de CV or Experts SAS
#############################################################################
#
#    Coded by: Marco Hernández (marco.hernandez@experts.com.mx)
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
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
from datetime import date, datetime, timedelta

class SaleAdvanceRel(models.Model):
    _name = 'sale.advanced.rel'

    invoice_rel_id = fields.Many2one('account.move','Anticipo', readonly=True, domain="[('id','=',False)]", copy=False)
    uuid_rel_inv = fields.Char('UUID relacionado', size=256, help="Se ingresa el folio fiscal UUID de la factura a la que se quiere relacionar este comprobante. Esto sera usado mayormente con saldos iniciales o facturas manuales", copy=False)
    amount_applied = fields.Float('Monto aplicado', default = 0.0, copy=False )
    sale_id = fields.Many2one('sale.order','Venta', copy=False)
    currency_id = fields.Many2one('res.currency', 'Moneda', related='invoice_rel_id.currency_id')

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    inv_advanced_ids = fields.One2many('sale.advanced.rel', 'sale_id',  'Anticipos')
    block_invoiced = fields.Boolean('Bloqueo de estado de facturación', default=False)

    def to_invoiced(self):
        self.write({'sale_invoice_status': 'invoiced','block_invoiced': True})
        return True

    @api.depends('state', 'order_line.invoice_status')
    def _get_invoice_status_2(self):
        rec =  super(SaleOrder,self)._get_invoice_status_2()
        for order in self:
            if order.block_invoiced == True:
                invoice_status = 'invoiced'
                order.sale_invoice_status = invoice_status


    @api.onchange('partner_id')
    def onchange_partner_adv_id(self):
        self.inv_advanced_ids = [(6,0,[])]
        res = {}
        if self.partner_id:
            # Se buscan los anticipos del cliente
            acc_inv_adv_ids = self.env['account.move.advanced'].search([('partner_id','=',self.partner_id.id),('state','=','open'),])
            # Si tiene anticipos
            if acc_inv_adv_ids:
                # Cargamos los anticipos
                aias = []
                for aia in acc_inv_adv_ids:
                    if aia.amount_residual > 0:
                        aias.append(aia.id)
                # Seleccionamos el primero
                if aias:
                    # self.account_invoice_advanced_id = aias[0]
                    res.update({'warning': {'title': _('Atención'), 'message': _('Este cliente tiene anticipos, se pueden agregar los anticipos aa laa venta en la pestaña de Anticipos.')}})

        # Se actualizan los impuestos de las lineas de venta al cambiar el cliente
        for sale in self:
            for line in sale.order_line:
                line._compute_tax_id()
        

        return res

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        today = datetime.strptime(fields.Date.today(), "%Y-%m-%d")
        # Actualizamos la fecha de caducidad según los dias de la compañia
        if self.env.user.company_id.quotation_expiration_days > 0:
            validity_date = today + timedelta(days=self.env.user.company_id.quotation_expiration_days)
            res.write({'validity_date': validity_date})
        else:
            res.write({'validity_date': today})
        return res

    
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(SaleOrder, self).onchange_partner_id()
        if self.partner_id:
            # Set as default the pricelist in sale
            value = {'pricelist_id':self.partner_id.property_product_pricelist}
            self.update(value)
        return res

    
    def action_confirm(self):
        for sale_row in self:
            for line_row in sale_row.order_line:
                if line_row.product_id.need_quote and line_row.price_unit == 0.0:
                    raise UserError(_('No se puede vender un producto que se necesita cotizar con un precio de $0.0.'))
        res = super(SaleOrder, self).action_confirm()
        return res


    def _prepare_invoice(self):
        for record in self:
            vals = super(SaleOrder, record)._prepare_invoice()
            # Si la venta tiene asociado un anticipo
            if record.inv_advanced_ids:
                adv_lines = []
                for adv_inv_row in record.inv_advanced_ids:
                    adv_vals = {
                        'invoice_rel_id': adv_inv_row.invoice_rel_id.id,
                        'uuid_rel_inv': adv_inv_row.uuid_rel_inv,
                        'amount_applied': adv_inv_row.amount_applied,
                    }
                    adv_lines.append((0,0,adv_vals))
                vals.update({'cfdi_type_rel':'07', 'invoice_advanced_rel_ids': adv_lines})
            return vals

    def get_amount_applied_cfdi_rel(self, adv_row):
        inv_residual = self.currency_id.with_context(date=self.date_order).compute(self.amount_total, adv_row.currency_id)
        if adv_row.amount_residual >= inv_residual:
            amount = inv_residual
        else:
            amount = adv_row.amount_residual
        return amount

    def create_sale_advance(self):
        self.ensure_one()
        # Se crea el wizard
        vals = {
            'partner_id': self.partner_id.id,
            'sale_id':self.id
        }
        wizard_id = self.env['select.sale.advanced.wizard'].create(vals)
       
        # Buscamos los anticipos del cliente
        domain = [('partner_id','=',self.partner_id.id),('state','=', 'open')]
        if not self.company_id.allow_advanced_multicurrency:
            domain.append(('currency_id','=',self.currency_id.id))
        advanced_rows = self.env['account.move.advanced'].search(domain)
        for advanced_row in advanced_rows:
            amount = self.get_amount_applied_cfdi_rel(advanced_row)
            val = {
                'wizard_id': wizard_id.id,
                'invoice_rel_id': advanced_row.invoice_id.id,
                'advanced_id': advanced_row.id,
                'selected': False,
                'amount_applied': amount,
            }
            self.env['sale.advanced.line'].create(val)
        # Devolvemos el wizard
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'select.sale.advanced.wizard',
            'views': [(self.env.ref('cqn_sale_extend.select_sale_advanced_wizard_id').id, 'form')],
            'res_id': wizard_id.id,
            'target': 'new',
        }

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    
    @api.onchange('price_unit')
    def onchange_price_unit(self):
        for record in self:
        # When the price_unit2 is lower than price_unit
            if record.price_unit and record.product_id:
                product = record.product_id.with_context(
                    lang=record.order_id.partner_id.lang,
                    partner=record.order_id.partner_id.id,
                    quantity= record.product_uom_qty,
                    date=record.order_id.date_order,
                    pricelist=record.order_id.pricelist_id.id,
                    uom=record.product_uom.id
                )
                price_unit = record.env['account.tax']._fix_tax_included_price_company(record._get_display_price(product), product.taxes_id, record.tax_id, record.company_id)
                if price_unit > record.price_unit:
                    record.price_unit = price_unit
                    return {
                            'warning': {
                                'title': 'Aviso!',
                                'message': u'El precio mínimo para este producto es: '+ str(price_unit)}
                            }
            return {}

    @api.onchange('product_id')
    def _onchange_product_id_check_need_quote(self):
        if not self.product_id:
            return {}
        if self.product_id.need_quote:
            warning_mess = {
                'title': _(u'Este producto necesita ser cotizado.!'),
                'message' : _('')
            }
            return {'warning': warning_mess}
        return {}
