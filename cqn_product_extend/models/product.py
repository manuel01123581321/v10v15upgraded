#    -*- encoding: utf-8 -*-
#####################################################################################
#    Module Writen to Odoo 10.0 Community Edition
#    All Rights Reserved to Experts SA de CV or Experts SAS
#####################################################################################
#
#    Coded by: Daniel Acosta (daniel.acosta@experts.com.mx)
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
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp
from odoo.osv import expression
from odoo.tools.float_utils import float_round
from datetime import datetime
import operator as py_operator

class ProductTemperature(models.Model):
    _name = 'product.temperature'

    name = fields.Char(string='Nombre')


class Product(models.Model):
    _inherit = 'product.template'

    def _compute_group(self):
        for row in self:
            if self.env.user.has_group('stock.group_stock_manager') or self.env.user.has_group('purchase.group_purchase_manager'):
                row.edit_temperature = True
            else:
                row.edit_temperature = False
        return True

    edit_temperature = fields.Boolean("Editar temperatura",compute='_compute_group')
    product_temperature_id = fields.Many2one('product.temperature',string='Temperatura')
    qty_available_only_stock_location = fields.Float(
        'Quantity On Hand', compute='_compute_quantities_stock', search='_search_qty_available',
        digits=dp.get_precision('Product Unit of Measure'))

    @api.depends(
        'product_variant_ids',
        'product_variant_ids.stock_quant_ids',
    )
    def _compute_quantities_stock(self):
        res = self._compute_quantities_dict_stock()
        for template in self:
            template.qty_available_only_stock_location = res[template.id]['qty_available']

    def _product_available_stock(self, name, arg):
        return self._compute_quantities_dict_stock()

    def _compute_quantities_dict_stock(self):
        # TDE FIXME: why not using directly the function fields ?
        variants_available = self.mapped('product_variant_ids')._product_available_stock()
        prod_available = {}
        for template in self:
            qty_available = 0
            for p in template.product_variant_ids:
                qty_available += variants_available[p.id]["qty_available"]
            prod_available[template.id] = {
                "qty_available": qty_available,
            }
        return prod_available

class ProductProduct(models.Model):
    _inherit = 'product.product'

    qty_available_only_stock_location = fields.Float(
        'Cantidad disponible en stock', compute='_compute_quantities_stock', search='_search_qty_available_stock',
        digits=dp.get_precision('Product Unit of Measure'),
        help="Cantidad disponible solo en las ubicaciones de Stock de los almacenes.")

    @api.depends('stock_quant_ids', 'stock_move_ids')
    def _compute_quantities_stock(self):
        res = self._compute_quantities_stock_dict(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'), self._context.get('from_date'), self._context.get('to_date'))
        for product in self:
            product.qty_available_only_stock_location = res[product.id]['qty_available']


    def _product_available_stock(self, field_names=None, arg=False):
        """ Compatibility method """
        return self._compute_quantities_stock_dict(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'), self._context.get('from_date'), self._context.get('to_date'))


    def _compute_quantities_stock_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        # Obtenemos las ubicaciones solo de stock
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations_stock()

        domain_quant = [('product_id', 'in', self.ids)] + domain_quant_loc
        dates_in_the_past = False
        if to_date and to_date < fields.Datetime.now(): #Only to_date as to_date will correspond to qty_available
            dates_in_the_past = True

        domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
        domain_move_out = [('product_id', 'in', self.ids)] + domain_move_out_loc
        if lot_id:
            domain_quant += [('lot_id', '=', lot_id)]
        if owner_id:
            domain_quant += [('owner_id', '=', owner_id)]
            domain_move_in += [('restrict_partner_id', '=', owner_id)]
            domain_move_out += [('restrict_partner_id', '=', owner_id)]
        if package_id:
            domain_quant += [('package_id', '=', package_id)]
        if dates_in_the_past:
            domain_move_in_done = list(domain_move_in)
            domain_move_out_done = list(domain_move_out)
        if from_date:
            domain_move_in += [('date', '>=', from_date)]
            domain_move_out += [('date', '>=', from_date)]
        if to_date:
            domain_move_in += [('date', '<=', to_date)]
            domain_move_out += [('date', '<=', to_date)]

        Move = self.env['stock.move']
        Quant = self.env['stock.quant']
        domain_move_in_todo = [('state', 'not in', ('done', 'cancel', 'draft'))] + domain_move_in
        domain_move_out_todo = [('state', 'not in', ('done', 'cancel', 'draft'))] + domain_move_out
        moves_in_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
        moves_out_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
        domain_quant += [('reservation_id','=',False)]
        quants_res = dict((item['product_id'][0], item['qty']) for item in Quant.read_group(domain_quant, ['product_id', 'qty'], ['product_id'], orderby='id'))
        if dates_in_the_past:
            # Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
            domain_move_in_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
            domain_move_out_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
            moves_in_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
            moves_out_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))

        res = dict()
        for product in self.with_context(prefetch_fields=False):
            res[product.id] = {}
            if dates_in_the_past:
                qty_available = quants_res.get(product.id, 0.0) - moves_in_res_past.get(product.id, 0.0) + moves_out_res_past.get(product.id, 0.0)
            else:
                qty_available = quants_res.get(product.id, 0.0)
            res[product.id]['qty_available'] = float_round(qty_available, precision_rounding=product.uom_id.rounding)
        return res

    def _get_domain_locations_stock(self):
        '''
        Solo obtenemos ubicaciones de stock de los almacenes
        '''
        Warehouse = self.env['stock.warehouse']

        location_ids = []
        
        if self.env.context.get('warehouse', False):
            if isinstance(self.env.context['warehouse'], (int, long)):
                wids = [self.env.context['warehouse']]
            elif isinstance(self.env.context['warehouse'], basestring):
                domain = [('name', 'ilike', self.env.context['warehouse'])]
                if self.env.context.get('force_company', False):
                    domain += [('company_id', '=', self.env.context['force_company'])]
                wids = Warehouse.search(domain).ids
            else:
                wids = self.env.context['warehouse']
        else:
            wids = Warehouse.search([]).ids

        for w in Warehouse.browse(wids):
            location_ids.append(w.lot_stock_id.id)
        return self._get_domain_locations_new(location_ids, company_id=self.env.context.get('force_company', False), compute_child=self.env.context.get('compute_child', True))


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def do_new_transfer(self):
        if self.picking_type_id.code == 'incoming':
            for line in self.pack_operation_product_ids:
                if not line.product_id.product_tmpl_id.product_temperature_id:
                    raise UserError(_("No se puede validar, el producto [ %s ] de la linea de operaciones, no tiene definido el campo temperatura" % line.product_id.product_tmpl_id.name))
        return super(StockPicking, self).do_new_transfer()
