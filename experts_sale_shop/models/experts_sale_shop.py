#!/usr/bin/env python
# -*- encoding: utf-8 -*- 
#############################################################################
#    Module Writen to Odoo 10 Community Edition
#    All Rights Reserved to Experts SA de CV or Experts SAS
#############################################################################
#
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
from odoo import api, fields, models, _ ,SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError

class SaleShop(models.Model):
    _name = 'sale.shop'

    name = fields.Char(string=u'Nombre de la tienda', size=100, required=True)
    ware_house_ids = fields.One2many('sale.shop.warehouse', 'shop_id', string="Almacenes",required=True, ondelete='CASCADE')
    users_ids = fields.Many2many('res.users','shop_user_rel','shop_id','user_id','Usuarios')
    sell_without_stock = fields.Boolean('Vender sin stock', default=True, help="Permite confirmar ventas sin producto completo en almacen.")
    automatic_pickings = fields.Boolean('Movimientos entre almacenes de tienda automaticos',default=True,help="Permite realizar los movimientos de los diferentes almacenes de la tienda en automatico para acompletar el almacen principal.")
    invoice_journal_id = fields.Many2one('account.journal', string="Diario de facturación", required=True, domain=[('type','=','sale')])
    remission_journal_id = fields.Many2one('account.journal', string="Diario de remisiones", required=True, domain=[('type','=','sale')])
    create_auto_invoice = fields.Boolean('Crear factura al confirmar venta',default=False)
    sequence_id = fields.Many2one('ir.sequence','Secuencia', required=True)
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Posición Fiscal')


    def get_qty_available_product_store(self, product_id):
        # Metodo para obtener la cantidad disponible de un producto en una tienda
        for record in self:
            product_obj = self.env['product.product']
            qty_available = 0.0
            if product_id:
                shop_row = record
                for warehouse_row in shop_row.ware_house_ids:
                    # Obtenemos la ubicacion de stock del almacen
                    location_row = warehouse_row.warehouse_id.lot_stock_id
                    product_row = product_obj.browse(product_id)
                    # Obtenemos la cantidad disponible en AG                
                    # Obtenemos la cantidad en el almacen
                    qty_mp_stock = product_row.with_context(location=[location_row.id]).qty_available
                    # Obtenemos la cantidad que esta apartada
                    qty_mp_outgoing = product_row.with_context(location=[location_row.id]).outgoing_qty
                    qty_mp_incoming = product_row.with_context(location=[location_row.id]).incoming_qty
                    real_qty = qty_mp_stock - qty_mp_outgoing + qty_mp_incoming
                    # Sumamos las cantidades disponibles de cada ubicacion
                    qty_available += real_qty
            return qty_available


    def get_qty_available_store(self, product_id):
        # Metodo para obtener la cantidad en mano la cantidad saliente, entrante y virtual del un producto por tienda
        for record in self:
            product_obj = self.env['product.product']
            qty_available = 0.0
            outgoing_qty = 0.0
            virtual_available= 0.0
            incoming_qty = 0.0
            if product_id and record:
                shop_row = record
                for warehouse_row in shop_row.ware_house_ids:
                    product_row = product_obj.browse(product_id)
                    # Obtenemos la ubicacion de stock del almacen
                    location_row = warehouse_row.warehouse_id.lot_stock_id
                    # Comprobamos la disponibilidad del producto en el alamcen elegido
                    qty_available += product_row.with_context(location=[location_row.id]).qty_available
                    outgoing_qty +=  product_row.with_context(location=[location_row.id]).outgoing_qty
                    virtual_available += product_row.with_context(location=[location_row.id]).virtual_available
                    incoming_qty += product_row.with_context(location=[location_row.id]).incoming_qty
            return {'qty_available': qty_available, 'outgoing_qty': outgoing_qty, 'virtual_available': virtual_available, 'incoming_qty': incoming_qty}

class SaleShopWarehouse(models.Model):
    _name = 'sale.shop.warehouse'

    @api.model
    def create(self, vals):
        #
        warehouse_ids = self.search([('warehouse_id','=',vals.get('warehouse_id')),('shop_id','=',vals.get('shop_id'))])
        if warehouse_ids:
            raise UserError (_('Error !\n\nEl almacén ya está en la lista !'))
        res= super(SaleShopWarehouse, self).create(vals)
        #
        warehouse_row = res
        if warehouse_row.sequence > 1 and not warehouse_row.location_dest_id:
            raise UserError (_('Debe seleccionar una ubicación de tránsito destino para las ubicaciones secundarias. !'))
        return res

    def _get_type(self):
        res = {}
        for row in self:
            if row.sequence == 1:
                row.type = "Primario"
            else:
                row.type = "Secundario"
        return res

    sequence = fields.Integer(string='Secuencia', required=True, readonly=True, default=1)
    warehouse_id = fields.Many2one('stock.warehouse', string=u'Almacén', required=True)
    shop_id = fields.Many2one('sale.shop', string="Sucursal", ondelete='CASCADE')
    location_dest_id = fields.Many2one('stock.location', string="Ubicación de tránsito destino")
    type = fields.Char(compute='_get_type', string="Tipo")
    
    _order = 'sequence asc, id desc'

    # @api.constrains('warehouse_id', 'shop_id')
    # def _check_single_shop(self):
    #     for shop_warehouse_row in self:
    #         shop_warehouse_other_row = self.search([('warehouse_id','=',shop_warehouse_row.warehouse_id.id),('shop_id','!=',shop_warehouse_row.shop_id.id)], limit=1)
    #         if shop_warehouse_other_row:
    #             raise ValidationError(_('No puedes agregar el amacen %s porque ya pertenece a la tienda %s.'%(shop_warehouse_row.warehouse_id.name,shop_warehouse_other_row.shop_id.name)))
    #     return True
