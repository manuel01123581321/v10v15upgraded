#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    CopyLeft 2012 - http://experts.com.mx
#    You are free to share, copy, distribute, transmit, adapt and use for commercial purpose
#    More information about license: http://www.gnu.org/licenses/agpl.html
#
#############################################################################
#
#    Coded by: Marco Hernández (marco.hernandez@experts.com.mx)
#    Coded by: Carlos Blanco (carlos.blanco@experts.com.mx)
#    Coded by: Mauricio Ruiz (mauricio.ruiz@experts.com.mx)
#
#############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import api, fields, models, _ ,SUPERUSER_ID
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_list(self):
        shops = []
        # Obtenemos las tiendas  a las que pertenece el usuario
        if self.env.user.shop_ids:
            for shop in self.env.user.shop_ids:
                shops.append(shop.id)
        return shops

    def _get_default_shop_2(self):
        if self.env.user.shop_id:
            return self.env.user.shop_id.id
        return False

    def _get_shops(self):
        shops = self._get_list()
        print(shops)
        return "[('id','in',[" + ','.join(map(str, list(shops))) + "])]"

    
    #shop_id = fields.Many2one('sale.shop', string="Tienda", required=True, default=_get_default_shop_2, domain=_get_shops,readonly=True, states={'draft': [('readonly', False)],'sent': [('readonly', False)]})
    shop_id = fields.Many2one('sale.shop', string="Tienda")
    #forma_pago_id = fields.Many2one('res.forma.pago', 'Forma de pago')
    #met_pago_id = fields.Many2one('res.met.pago', 'Método de pago')
    acc_payment = fields.Many2one('res.partner.bank', 'Numero de Cuenta')

    
    
    @api.onchange('partner_shipping_id', 'partner_id')
    def onchange_partner_shipping_id(self):

        """
        Trigger the change of fiscal position when the shipping address is modified.
        """
        fiscal_position_id = self.env['account.fiscal.position'].get_fiscal_position(self.partner_id.id, self.partner_shipping_id.id)
        if fiscal_position_id:
            self.fiscal_position_id = fiscal_position_id
        elif self.shop_id:
            if self.shop_id.fiscal_position_id:
                self.fiscal_position_id = self.shop_id.fiscal_position_id.id
            else:
                self.fiscal_position_id = fiscal_position_id
        else:
            self.fiscal_position_id = fiscal_position_id
        return {}

    @api.onchange('shop_id')
    def onchange_shop_id(self):
        res = {}
        if not self.shop_id:
            self.warehouse_id = False
            return {}
        if self.shop_id.fiscal_position_id:
            self.fiscal_position_id = self.shop_id.fiscal_position_id.id
        if self.shop_id.ware_house_ids:
            self.warehouse_id = self.shop_id.ware_house_ids[0].warehouse_id.id

        else:
            warning = {
                'title': _('Configuracion de Sucursal'),
                'message' : _(u'No se tienen seleccionados almacenes para la sucursal seleccionada.')
            }
            res['warning'] = warning
        return res

    
    def action_invoice_create_auto_shop(self, grouped=False, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        inv_obj = self.env['account.move']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoices = {}
        references = {}
        for order in self:
            group_key = order.id if grouped else (order.partner_invoice_id.id, order.currency_id.id)
            for line in order.order_line:
                if group_key not in invoices:
                    inv_data = order._prepare_invoice()
                    invoice = inv_obj.create(inv_data)
                    references[invoice] = order
                    invoices[group_key] = invoice
                elif group_key in invoices:
                    vals = {}
                    if order.name not in invoices[group_key].origin.split(', '):
                        vals['origin'] = invoices[group_key].origin + ', ' + order.name
                    if order.client_order_ref and order.client_order_ref not in invoices[group_key].name.split(', ') and order.client_order_ref != invoices[group_key].name:
                        vals['name'] = invoices[group_key].name + ', ' + order.client_order_ref
                    invoices[group_key].write(vals)
                line.invoice_line_create(invoices[group_key].id, line.product_uom_qty)

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoice] = references[invoice] | order
        if not invoices:
            raise UserError(_('No hay lineas para faturar.'))

        for invoice in invoices.values():
            if not invoice.invoice_line_ids:
                raise UserError(_('No hay lineas para facturar.'))
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_untaxed < 0:
                invoice.type = 'out_refund'
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity
            # Use additional field helper function (for account extensions)
            for line in invoice.invoice_line_ids:
                line._set_additional_fields(invoice)
            # Necessary to force computation of taxes. In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create.
            invoice.compute_taxes()
            invoice.message_post_with_view('mail.message_origin_link',
                values={'self': invoice, 'origin': references[invoice]},
                subtype_id=self.env.ref('mail.mt_note').id)
        return [inv.id for inv in invoices.values()]

    
    def action_confirm(self):
        # redefinimos el metodo para crear los movimientos de almacen si es necesario para los productos vendidos
        picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        shop_obj = self.env['sale.shop']
        product_obj = self.env['product.product']
        picking_ids = []
        # Recorremos cada venta para realizar os movimientos de almacen correspondientes
        for sale_row in self:
            # Actualizamo el almacen de la tienda en la venta por si tiene alguno diferente
            if sale_row.shop_id:
                if self.warehouse_id != self.shop_id.ware_house_ids[0].warehouse_id:
                    self.warehouse_id = self.shop_id.ware_house_ids[0].warehouse_id.id
            if not sale_row.shop_id.ware_house_ids:
                raise UserError (_('Error !\n\nNo se han seleccionado almacenes para la sucursal %s!'%(sale_row.shop_id and sale_row.shop_id.name or '-',)))
            main_location_row = sale_row.shop_id.ware_house_ids[0].warehouse_id.lot_stock_id
            for sale_line_row in sale_row.order_line:
                qty_total = sale_line_row.product_uom_qty
                picking_location_ids = {}
                if sale_line_row.product_id:
                    if sale_line_row.product_id.type == 'product':
                        # Verificamos si nos alcanza el material para enviar al almacen principal
                        qty_available_total = sale_row.shop_id.get_qty_available_product_store(sale_line_row.product_id.id)
                        if qty_available_total >= sale_line_row.product_uom_qty:
                            # Comprobamos la disponibilidad del producto en el alamcen elegido
                            qty_available = sale_line_row.product_id.sudo().with_context(location=[main_location_row.id]).virtual_available
                            if qty_total > qty_available and sale_row.shop_id.automatic_pickings:
                                qty_total -= qty_available
                                for warehouse_row in sale_row.shop_id.ware_house_ids:
                                    picking_id = False
                                    # Obtenemos la ubicacion de stock del almacen
                                    location_row = warehouse_row.warehouse_id.lot_stock_id
                                    if location_row.id != main_location_row.id:
                                        # Obtenemos la cantidad disponible en AG
                                        # Comprobamos la disponibilidad del producto en el alamcen elegido
                                        qty_available = sale_line_row.product_id.sudo().with_context(location=[location_row.id]).virtual_available
                                        # Sumamos las cantidades disponibles de cada ubicacion
                                        qty_available = qty_location[sale_line_row.product_id.id].get('virtual_available')
                                        if qty_available > 0:
                                            if qty_available < qty_total:
                                                if not picking_location_ids.get(location_row.id):
                                                    picking_vals = self.sudo()._prepare_picking_shop('internal', 'internal', warehouse_row.warehouse_id.id, location_row.id, main_location_dest_row.id, sale_row.name)
                                                    picking_id = picking_obj.create(picking_vals)
                                                    picking_location_ids.update({location_row.id:picking_id.id})
                                                    picking_ids += picking_id
                                                else:
                                                    picking_id = picking_location_ids.get(location_row.id)
                                                move_vals = self.sudo()._prepare_move_shop(sale_line_row.product_id, qty_available, picking_id.id, location_row.id, main_location_dest_row.id)
                                                move_obj.create(move_vals)
                                                qty_total -= qty_available
                                            elif qty_available >= qty_total:
                                                if not picking_location_ids.get(location_row.id):
                                                    picking_vals = self.sudo()._prepare_picking_shop('internal', 'internal', warehouse_row.warehouse_id.id, location_row.id, main_location_dest_row.id, sale_row.name)
                                                    picking_id = picking_obj.create(picking_vals)
                                                    picking_location_ids.update({location_row.id:picking_id})
                                                    picking_ids += picking_id
                                                else:
                                                    picking_id = picking_location_ids.get(location_row.id)
                                                move_vals = self.sudo()._prepare_move_shop(sale_line_row.product_id, qty_total, picking_id.id, location_row.id, main_location_dest_row.id)
                                                move_obj.create(move_vals)
                                                qty_total = 0.0
                                                break
                        else:
                            if not sale_row.shop_id.sell_without_stock:
                                raise UserError (_(u'Error !\n\nNo tienes suficiente producto en almacén para surtir la venta !'))
        if picking_ids:
            self.confirm_picking(picking_ids)
        res = super(SaleOrder, self).action_confirm()

        for sale_row in self:
            if sale_row.shop_id.create_auto_invoice:
                sale_row.action_invoice_create_auto_shop()
                for invoice_row in sale_row.invoice_ids:
                    invoice_row.action_invoice_open()
                self.invoice_status = 'invoiced'
        return res

    def _prepare_invoice(self):
        inv_vals = super(SaleOrder, self)._prepare_invoice()
        currency_id = self.shop_id.remission_journal_id.currency_id and self.shop_id.remission_journal_id.currency_id.id or self.shop_id.remission_journal_id.company_id.currency_id.id
        inv_vals.update({'shop_id': self.shop_id.id, 'journal_id': self.shop_id.remission_journal_id.id, 'met_pago_id': self.met_pago_id and self.met_pago_id.id or False,'forma_pago_id': self.forma_pago_id and self.forma_pago_id.id or False, 'acc_payment': self.acc_payment and self.acc_payment.id or False})
        if inv_vals.get('currency_id') != currency_id:
           inv_vals.update({'currency_id': currency_id})
        return inv_vals

    def confirm_picking(self, picking_ids):
        """
        Método para contefirmar el picking
        """
        picking_ids.action_confirm()
        picking_ids.action_assign()
        return True

    def _prepare_picking_shop(self, code, type_pick, warehouse_id, location_id, location_dest_id,  origin):
        """
        Método para obtener los datos necesarios para crear un Picking
        """
        picking_type_ids = self.env['stock.picking.type'].search([('code','=', code),('warehouse_id','=',warehouse_id)], limit=1)
        if not picking_type_ids:
            raise UserError (_(u'Error !\n\nNo existe tipo de movimiento de almacén !'))
        return {
            'origin': origin,
            'type': type_pick,
            'state': 'draft',
            'move_type': 'direct',
            'picking_type_id': picking_type_ids.id,
            'invoice_state': 'none',
            'location_id': location_id,
            'location_dest_id': location_dest_id,
        }

    def _prepare_move_shop(self, product_row, qty, picking_id, location_id, location_dest_id):
        """
        Método para crear el diccionario con los valores para crear el stock.move
        """
        product_uom_id = product_row.uom_id.id
        vals = {
            'name': product_row.name,
            'picking_id': picking_id,
            'product_id': product_row.id,
            'product_uom': product_uom_id,
            'product_uos_qty': qty,
            'product_uom_qty': qty,
            'product_uos': product_uom_id,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'tracking_id': False,
            'state': 'draft',
        }
        return vals

    
    @api.onchange('partner_id')
    def onchange_partner_shop_id(self):
        res = {}
        if self.partner_id:
            partner_bank_obj = self.env['res.partner.bank']
            payment_term=False
            form_term = False
            payment_term = self.partner_id.met_pago_id and self.partner_id.met_pago_id.id or False
            form_term = self.partner_id.forma_pago_id and self.partner_id.forma_pago_id.id or False
            self.met_pago_id = payment_term
            self.forma_pago_id = form_term
        return res

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New') and vals.get('shop_id'):
            shop_row = self.env['sale.shop'].browse(vals.get('shop_id'))
            if shop_row.sequence_id:
                if 'company_id' in vals:
                    vals['name'] = shop_row.sequence_id.with_context(force_company=vals['company_id']).next_by_id() or _('New')
                else:
                    vals['name'] = shop_row.sequence_id.next_by_id() or _('New')
        result = super(SaleOrder, self).create(vals)
        return result

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        substitutes = []
        res = {}
        if not self.product_id or not self.product_uom_qty or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.type == 'product':
            locations_ids = []
            env = api.Environment(self._cr, SUPERUSER_ID, {})
            shop_row = env['sale.shop'].browse(self.order_id.shop_id.id)
            for warehouse_row in shop_row.ware_house_ids:
                # Obtenemos la ubicacion de stock del almacen
                locations_ids.append(warehouse_row.warehouse_id.lot_stock_id.id)
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
            if float_compare(self.product_id.sudo().with_context(location=locations_ids).qty_available-self.product_id.sudo().with_context(location=locations_ids).outgoing_qty, product_qty, precision_digits=precision) == -1:
                is_available = self._check_routing()
                if not is_available and not self.company_id.prevent_product_exists_warning:
                    msj_qty_available = self.product_id.sudo().with_context(location=locations_ids).qty_available-self.product_id.sudo().with_context(location=locations_ids).outgoing_qty
                    if msj_qty_available < 0:
                        msj_qty_available = 0.0
                    warning_mess = {
                        'title': _(u'No hay suficiente inventario!'),
                        'message' : _(u'Usted planea vender %s %s pero solo se tienen %s %s disponibles!\nEl stock real es de %s %s y vienen en camino %s %s') % \
                            (self.product_uom_qty, self.product_uom.name, msj_qty_available , self.product_id.uom_id.name, self.product_id.with_context(location=locations_ids).qty_available, self.product_id.uom_id.name, self.product_id.with_context(location=locations_ids).incoming_qty, self.product_id.uom_id.name)
                    }

                    # Productos substituto
                    substitute_obj = self.env['substitute.products']
                    # Obtenemos los productos substitutos con existencia real mayor a 0
                    substitute_rows = substitute_obj.search([('product_id','=',self.product_id.product_tmpl_id.id)])
                    # Para cada producto
                    for substitute in substitute_rows:
                        # Obtenemos la cantidad real en los almacenes configurados en experts_sale_shop
                        qty_real_sub = shop_row.get_qty_available_product_store(substitute.substitute_id.id)
                        # Si el producto tiene existencias
                        if qty_real_sub > 0:
                            substitutes.append(substitute.id)
                    # Actualizamos el domain
                    res.update({'domain':{'substitute_ids':[('id','in',substitutes)]}, 'warning': warning_mess})
                    # return {'domain': {'product_uom': [('category_id', '=', product.uom_id.category_id.id)]}}
                    return res
        return res


    qty_available = fields.Float(string='Existencia')
    substitute_ids =  fields.Many2one('substitute.products',"Substitutos")
