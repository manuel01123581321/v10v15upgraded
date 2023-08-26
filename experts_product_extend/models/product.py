# -*- encoding: utf-8 -*-
#############################################################################
#    Module Writen to Odoo 10 Community Edition
#    All Rights Reserved to Experts SA de CV or Experts SAS
#############################################################################
#
#    Coded by: Eric Hernández (eric.hernandez@experts.com.mx)
#    Coded by: Carlos Blanco (carlos.blanco@experts.com.mx)
#    Migrated by: Carlos Blanco (carlos.blanco@experts.com.mx)
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

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp

class ProductCategory(models.Model):
    _inherit = "product.category"

    ref = fields.Char('Referencia', size=64)

class ProductBrand(models.Model):
    _name = "product.brand"
    _description="Marca de producto"

    name = fields.Char('Nombre', size=64, required=True)
    description = fields.Text('Descripción')

class ProductTemplate(models.Model):
    _inherit = "product.template"

    group_id = fields.Many2one('product.group',string='Grupo')
    sub_group_id = fields.Many2one('product.sub.group',string='Subgrupo')

    def validate_default_code(self,default_code):
        # Si especifican default_code
        if default_code:
            # Si se debe validar la referencia interna única
            if self.env.user.company_id.internal_reference_unique:
                # Validamos que no exista
                product_ids = self.search([('default_code','=',default_code.strip())])
                if product_ids:
                    raise UserError (_('Ya existe un producto con esta referencia interna.'))
        return True

    @api.model
    def create(self, vals):
        default_code = vals.get('default_code')
        self.validate_default_code(default_code)
        rec = super(ProductTemplate, self).create(vals)
        return rec

    @api.one
    def write(self, vals):
        default_code = vals.get('default_code')
        if default_code:
            self.validate_default_code(default_code)
        res = super(ProductTemplate, self).write(vals)
        return res


    def _get_stock_value(self):
        for product_row in self:
            product_row.stock_value = product_row.standard_price * product_row.qty_available    


    def _get_barcode_config(self):
        for product_row in self:
            if self.env.user.company_id.show_barcode_in_tree_view:
                product_row.show_barcode_in_tree_view = True

    brand_id = fields.Many2one( 'product.brand', 'Marca')
    model = fields.Char('Modelo', size=64)
    stock_value =fields.Float(compute=_get_stock_value, string="Valor de stock")
    volume = fields.Float('Volume',digits=dp.get_precision('Volume'), compute='_compute_volume', inverse='_set_volume',help="The volume in m3.", store=True)
    show_barcode_in_tree_view = fields.Boolean(string='Mostrar código de barras',compute='_get_barcode_config',default=False)

class Product(models.Model):
    _inherit = "product.product"


    def _get_stock_value_variant(self):
        for product_row in self:
            product_row.stock_value_varian = product_row.standard_price * product_row.qty_available

    stock_value_varian = fields.Float(compute=_get_stock_value_variant, string="Valor de stock")

class ProductGroup(models.Model):
    _name = "product.group"

    name = fields.Char(string='Nombre')

class ProductSubGroup(models.Model):
    _name = "product.sub.group"

    name = fields.Char(string='Nombre')

class product_price_list(models.TransientModel):
    _inherit = 'product.price_list'
    _description = 'Price List'


    def print_report(self):
        datas = {'ids': self.env.context.get('active_ids', [])}
        # Si el wizard es llamado desde el objeto product.template se buscan las ids para el objeto product.product
        if self._context.get("use_product_template_model") :
            product_row = self.env['product.product'].search([('product_tmpl_id','in',self.env.context.get('active_ids', []))])
            if product_row:
                datas = {'ids': product_row.mapped('id')}
        res = self.read(['price_list', 'qty1', 'qty2', 'qty3', 'qty4', 'qty5'])
        res = res and res[0] or {}
        res['price_list'] = res['price_list'][0]
        datas['form'] = res
        return self.env['report'].get_action([], 'product.report_pricelist', data=datas)

