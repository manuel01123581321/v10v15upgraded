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

{
    "name": "Mejora a productos",
    "version": "1.0",
    "depends": ["base","product","stock_account","stock","experts_groups",'sale','stock_available_unreserved'],
    "author": "experts.com.mx",
    "category": "Stock Modules",
    "website" : "experts.com.mx",
    "description": """
        Este módulo extiende la funcionalidad de los productos:
            - Se agregó modelo al producto, este es un campo de texto.
            - Se agregó marca al producto, este es un catálogo y puede ser editado en la configuración de productos en ventas (Ventas -> Configuración -> Productos -> Marcas de productos).
            - Se agregó un permiso para permitir o no editar la referencia interna del producto.
            - Se agregó un permiso para permitir o no actualizar las existencias desde el producto.
            - Se agregó un permiso para permitir o no solicitar abastecimiento desde el producto.
            - Se agregó un permiso para permitir o no visualizar el precio de costo tanto en la vista lista como en la vista formulario, además que si pueden ver el precio de costo se puede ver en la vista lista un cálculo de valor de stock.
            - Se agregó un permiso para permitir o no editar el precio de lista del producto.
            - En la configurción de la compañía puede especificarse si la referencia interna del producto es única y si será requerida de manera obligatoria.
            - El campo volumen soporta una presición decimal configurable.
            - Agrega una configuración en la compañía para mostrar el código de barras en la vista lista de los productos en inventario
            - Se agregó un menu para crear  grupos y subgrupos en la configuración de ventas
            - Se agregó un permiso para permitir o no, visualizar y crear grupos y subgrupos 
            - Agrega la opción para imprimir el precio de los productos en el reporte de lista de precios
            - Agrega un botón para exportar la lista de precios a excel (.xls)
        Si tiene dudas, quiere reportar algún error o mejora póngase en contacto con nosotros: info@experts.com.mx
    """,
    "data" :[
        "views/assets.xml",
        "security/ir.model.access.csv",
        "security/groups.xml",
        "views/product_view.xml",
        "views/group_view.xml",
        "views/res_company_view.xml",
        "data/decimal_presicion.xml",
        "wizard/product_pricelist_inh_view.xml",
        ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': False,
    'price': 699,
    'currency': 'MXN',
}
