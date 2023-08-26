# -*- encoding: utf-8 -*-
#####################################################################################
#    Module Writen to Odoo 8.0 Community Edition
#    All Rights Reserved to Experts SA de CV or Experts SAS
#####################################################################################
#
#    Coded by: Carlos Blanco (carlos.blanco@experts.com.mx)
#    Coded by: Rodolfo Lopez (rodolfo.lopez@experts.com.mx)
#    Revised by: Eric Hernández (eric.hernandez@experts.com.mx)
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

from odoo import api, fields, models, _ ,SUPERUSER_ID
import time

class PartnerInvoiceWizard(models.TransientModel):
    _inherit = 'partner.invoice.wizard'

    """ TODO: Revisar con Carlos y Micho
        Esta de más el diario de remisión y factura en la tienda, realmente ningún cliente remisiona mas que ARCE.
        Si no queremos perder la funcionalidad de remisiones propongo: 
        *. Dos secuencias en el mismo diario, al valida duna factura toma secuencia de remisión y al timbrar la factura
           tomaría secuencia de factura.
    """
   
    def create_cfdi(self):
        # Objetos
        invoice_obj = self.env['account.move']
        wizard_row = self
        sale_obj =self.env['sale.order']
        if wizard_row.invoice_id.type=='out_invoice' and not self.env.context.get('not_change_journal'):
            if wizard_row.invoice_id.shop_id:
                # Solo se hacen los cambios si la moneda es MXN para que funcione para atrás, en las facturas en otra moneda no se realiza
                if wizard_row.invoice_id.journal_id.id != wizard_row.invoice_id.shop_id.invoice_journal_id.id and wizard_row.invoice_id.currency_id.name == 'MXN':
                    # Cancelamos la factura
                    wizard_row.invoice_id.action_invoice_cancel()
                    # La cambiamos a borrador
                    wizard_row.invoice_id.action_invoice_draft()
                    # Validamos la Factura
                    currency_id = wizard_row.invoice_id.shop_id.invoice_journal_id.currency_id and wizard_row.invoice_id.shop_id.invoice_journal_id.currency_id.id or wizard_row.invoice_id.shop_id.invoice_journal_id.company_id.currency_id.id
                    wizard_row.invoice_id.write({'invoice_datetime':time.strftime('%Y-%m-%d %H:%M:%S'),'move_name': False, 'journal_id':wizard_row.invoice_id.shop_id.invoice_journal_id.id,
                     'currency_id':currency_id,'met_pago_id':wizard_row.pay_method_id.id,'forma_pago_id':wizard_row.pay_forma_id.id})
                    wizard_row.invoice_id.action_invoice_open()
                    for line_inv_row in wizard_row.invoice_id.invoice_line_ids:
                        for sale_line_row in line_inv_row.sale_line_ids:
                            if sale_line_row.order_id not in sale_obj:
                                sale_obj += sale_line_row.order_id
                    if sale_obj:
                        for row in sale_obj:
                            row.invoice_status = 'invoiced'
        res = super(PartnerInvoiceWizard, self).create_cfdi()
        return res
