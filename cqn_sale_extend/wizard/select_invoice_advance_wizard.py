# -*- encoding: utf-8 -*-
#####################################################################################
#    Module Writen to Odoo 10.0 Community Edition
#    All Rights Reserved to Experts SA de CV or Experts SAS
#####################################################################################
#
#    Coded by: Mauricio Ruiz (mauricio.ruiz@experts.com.mx)
#
#####################################################################################
#    This software and associated files (the "Software") can only be used (executed,
#    modified, executed after modifications) with a valid purchase of these module
#    with Experts SA de CV or Experts SAS.
#
#    You may develop Odoo modules that use this Software as a library (typically by
#    depending on it, importing it and using its resources), but without copying any
#    source code or material from the Software.
#
#    You may distribute those modules under the license of your choice, provided
#    that this license is compatible with the terms of this license.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software or modified copies of the Software.
#
#    The above copyright notice and this permission notice must be included in all
#    copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#    SOFTWARE.
#####################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare

class SaleAdvancedLine(models.TransientModel):
    _name = 'sale.advanced.line'

    wizard_id = fields.Many2one('select.sale.advanced.wizard','Wizard', )
    uuid_rel_inv = fields.Char('UUID relacionado', size=256, help="Se ingresa el folio fiscal UUID de la factura a la que se quiere relacionar este comprobante. Esto sera usado mayormente con saldos iniciales o facturas manuales", copy=False)
    invoice_rel_id = fields.Many2one('account.move','Anticipo', readonly=True)
    advanced_id = fields.Many2one('account.invoice.advanced','Anticipo', readonly=True)
    amount = fields.Float('Monto',related='advanced_id.amount',readonly=True)
    amount_residual = fields.Float('Disponible',related='advanced_id.amount_residual',readonly=True)
    amount_applied = fields.Float('Monto a aplicar',default= 0.0)
    currency_id = fields.Many2one('res.currency','Moneda', related='advanced_id.currency_id',readonly=True)
    selected = fields.Boolean('Seleccionar', default=True)

class SelectInvoiceAdvancedWizard(models.TransientModel):
    _name = 'select.sale.advanced.wizard'

    partner_id = fields.Many2one('res.partner', 'Cliente', readonly=True,)
    sale_id = fields.Many2one('sale.order','venta', readonly=True)
    invoice_advanced_line_ids =  fields.One2many('sale.advanced.line', 'wizard_id' ,'Anticipos',)

    def select_advance(self):
        # Validamos los montos y moneda
        adv_rel_obj = self.env['sale.advanced.rel']
        advanced_rel_rows = adv_rel_obj.search([('sale_id','=',self.sale_id.id)])
        if advanced_rel_rows:
            advanced_rel_rows.unlink()
        amount_applied = 0.0
        if self.sale_id.state == 'done':
            raise UserError (_('La venta esta realizada no puedes agregar anticipos.'))
        for line in self.invoice_advanced_line_ids:
            vals = {}
            if not line.selected:
                continue
            amount_applied += line.amount_applied
            if float_compare(line.amount_applied, line.amount_residual, precision_digits=3) == 1:
            # ~ if line.amount_applied > line.amount_residual:
                raise UserError (_('El monto a aplicar no puede ser mayor a %s %s para el anticipo %s'%(line.amount_residual,line.invoice_rel_id.currency_id.name,line.invoice_rel_id.number)))
            inv_residual = self.sale_id.currency_id.with_context(date=self.sale_id.date_order).compute(self.sale_id.amount_total, line.advanced_id.currency_id)
            if float_compare(amount_applied, inv_residual, precision_digits=3) == 1:
            # ~ if amount_applied > inv_residual:
                raise UserError (_('El monto a aplicar no puede ser mayor a %s %s para la factura %s'%(self.sale_id.amount_total,self.sale_id.currency_id.name,self.sale_id.name)))
            vals.update({'sale_id': self.sale_id.id})
            if line.invoice_rel_id:
                vals.update({'invoice_rel_id': line.invoice_rel_id.id, 'uuid_rel_inv': line.invoice_rel_id.cfdi_folio_fiscal, 'amount_applied': line.amount_applied })
            else:
                vals.update({'uuid_rel_inv': line.uuid_rel_inv})
            adv_rel_obj.create(vals)
        return True


