#    -*- encoding: utf-8 -*- 
#####################################################################################
#    Module Writen to Odoo 10.0 Community Edition
#    All Rights Reserved to Experts SA de CV or Experts SAS
#####################################################################################
#
#    Coded by: Daniel Acosta (daniel.acosta@experts.com.mx)
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
###################################################################################
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError
from datetime import date,datetime
from xlwt import Workbook, Formula, easyxf
import StringIO
import xlwt
import tempfile
from tempfile import TemporaryFile
import base64

class product_price_list(models.TransientModel):
    _inherit = 'product.price_list'
    _description = 'Price List'

    show_product_cost = fields.Boolean('Mostrar el costo del producto', default=False)
    file = fields.Many2one('ir.attachment','Archivo', readonly=True)
    datas_fname = fields.Char('File Name')
    download_file = fields.Binary(related='file.datas', string='Archivo', help='')

    def export_xls(self):
        """
            Exportar lista de precios a excel 
        """
        attachment_obj = self.env['ir.attachment']
        # Hacemos referencia al reporte para obtener las lineas de productos
        report_pricelist_obj = self.env['report.product.report_pricelist']
        pricelist = self.env['product.pricelist'].browse(self.price_list[0].id)
        products = self.env['product.product'].search([('product_tmpl_id','in',self._context.get('active_ids'))])
        quantities = report_pricelist_obj._get_quantity(self.get_data())

        # Instanciamos el workbook
        book = Workbook(encoding='utf-8')
        buf = StringIO.StringIO()
        # Se definen colores
        xlwt.add_palette_colour("title_colour", 0x21)
        book.set_colour_RGB(0x21, 242, 242, 242)
        # lista de tuplas para coincidir en el merge_range de los titulos
        abc = [('A',1),('B',2),('C',3),('D',4),('E',5),('F',6),('G',7),('H',8),('I',9),('J',10)]
        qty_range = [('%s Unidad(es)'%self.qty1, self.qty1), 
                    ('%s Unidad(es)'%self.qty2, self.qty2), 
                    ('%s Unidad(es)'%self.qty3, self.qty3), 
                    ('%s Unidad(es)'%self.qty4, self.qty4), 
                    ('%s Unidad(es)'%self.qty4, self.qty4)]
        # Ordeneamos las unidades de acuerdo a la cantidad
        qty_range.sort(key=lambda tup: tup[1])
        after_qty_col = len(filter(lambda x: x[1]>0, qty_range))
        # Se definen las cabeceras y estilos
        style_title = easyxf('font: height 350, color black,bold on; alignment: horizontal center; pattern: pattern solid, fore_colour title_colour')
        styleb = easyxf('font: height 190, color black,bold on; alignment: horizontal center; pattern: pattern solid, fore_colour title_colour;borders: left thin, right thin, top thin, bottom thin; ')
        style_bold = easyxf('font: height 190, color black,bold on;')
        style_text = easyxf('font: height 170, color black; alignment: horizontal center;borders: left thin, right thin, top thin, bottom thin; ')
        row_range = after_qty_col + 3 if self.show_product_cost else after_qty_col
        # Nombre de la hoja
        sheet1 = book.add_sheet('Lista de precios')
        # Establecemos el ancho de columnas
        sheet1.col(0).width = 256 * 50
        sheet1.col(row_range - 1).width = 256 * 30
        sheet1.col(row_range).width = 256 * 20
        # Escribimos en los titulos
        sheet1.write_merge(0,0,0,row_range,'Lista de precios', style_title)
        sheet1.write(1,0,'Nombre de la tarifa', style_bold)
        sheet1.write(2,0,'Moneda', style_bold)
        sheet1.write(3,0,'Fecha de impresión', style_bold)
        # Valores de la lista de precios
        sheet1.write(1,1,self.price_list.name)
        sheet1.write(2,1,self.price_list.currency_id.name)
        sheet1.write(3,1,str(datetime.today()))

        # Titulos para las columnsas
        sheet1.write(5,0,'Descripción',styleb)
        for x in xrange(0,len(filter(lambda o: o[1] > 0,qty_range))):
            # Escirbimos los titulos de las cantidades
            sheet1.write(5, x + 1, filter(lambda o: o[1] > 0,qty_range)[x][0], styleb)

        if self.show_product_cost:
            sheet1.write(5, after_qty_col + 1, 'Costo', styleb)
            sheet1.write(5, after_qty_col + 2, 'Proveedor', styleb)
            sheet1.write(5, after_qty_col + 3, 'Precio proveedor', styleb)

        col = 1
        row = 6
        #product_rows = self.env['product.product'].search([('product_tmpl_id','in',self._context.get('active_ids'))])
        for categ_data in report_pricelist_obj._get_categories(pricelist, products, quantities):
            sheet1.write(row,0,categ_data.get('category').name, style_bold)
            row += 1
            for product in categ_data.get('products'):
                sheet1.write(row,0,'[%s] %s'%(product.code, product.name), style_text)
                # Escribimos las cantidades 
                for quantity in quantities:
                    sheet1.write(row,col,categ_data['prices'][product.id][quantity], style_text)
                    col += 1
                # Si esta activdo mostrar el costo del producto
                if self.show_product_cost:
                    # Costo de producto
                    sheet1.write(row, col, '%s '%str(self.price_list.currency_id.symbol) + '{:0,.2f}'.format(product.product_tmpl_id.standard_price), style_text)
                    for seller in product.seller_ids:
                        seller_name = ''
                        if seller.name:
                            parent_name = seller.name.parent_id.name if seller.name.parent_id else ''
                            seller_name = seller.name.name if seller.name.name and seller.name.name != ' ' else parent_name
                        # Proveedor y su respectivo costo
                        sheet1.write(row,col + 1, seller_name, style_text)
                        sheet1.write(row,col + 2, '%s '%str(self.price_list.currency_id.symbol) + '{:0,.2f}'.format(seller.price), style_text)
                        # Si tiene varios proveedores se hace un salto a la siguiente fila
                        if len(product.seller_ids) > 1:
                            row += 1
                col = 1
                row += 1

        new = 'Lista de precios - %s'%date.today() + '.xls'
        book.save(new)
        book.save(TemporaryFile())
        file = open(new,'rb')

        buf.close()
        data_attach = {
            'name': 'Lista de precios',
            'datas': base64.encodestring(file.read()),
            'datas_fname': new,
            'description': 'Lista',
            'res_model': 'product.price_list',
            'res_id': self.id,
        }
        attach = attachment_obj.create(data_attach)
        self.write({'file':attach.id,'datas_fname':new})
        file.close()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.price_list',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': self._context,
        }

    def get_data(self):
        datas = {'ids': self.env.context.get('active_ids', [])}
        res = self.read(['price_list', 'qty1', 'qty2', 'qty3', 'qty4', 'qty5'])
        res = res and res[0] or {}
        res['price_list'] = res['price_list'][0]
        datas['form'] = res
        datas['show_product_cost'] = self.show_product_cost
        return datas


    def print_report(self):
        """
        To get the date and print the report
        @return : return report
        """
        datas = self.get_data()
        return self.env['report'].get_action([], 'product.report_pricelist', data=datas)


class report_product_pricelist(models.AbstractModel):
    _inherit = 'report.product.report_pricelist'

    def get_supplier_price(self,product_id=None):
        product_row = self.env['product.template'].browse(product_id)
        lines = []
        if product_row:
            for line in product_row.seller_ids:
                name = ''
                if line.name:
                    parent_name = line.name.parent_id.name if line.name.parent_id else ''
                    name = line.name.name if line.name.name and line.name.name != ' ' else parent_name
                vals = {
                    'supplier_name': name,
                    'price': line.price,}
                lines.append(vals)
        return lines

    @api.model
    def render_html(self, docids, data=None):
        data = data if data is not None else {}
        pricelist = self.env['product.pricelist'].browse(data.get('form', {}).get('price_list', False))
        products = self.env['product.product'].search([('product_tmpl_id','in',data.get('ids', data.get('active_ids')))])
        quantities = self._get_quantity(data)
        docargs = {
            'doc_ids': data.get('ids', data.get('active_ids')),
            'doc_model': 'product.pricelist',
            'docs': products,
            'get_supplier_price': self.get_supplier_price,
            'data': dict(
                data,
                show_product_cost_report = data.get("show_product_cost"),
                pricelist=pricelist,
                quantities=quantities,
                categories_data=self._get_categories(pricelist, products, quantities)
            ),
        }
        return self.env['report'].render('product.report_pricelist', docargs)