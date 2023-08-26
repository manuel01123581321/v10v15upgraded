# -*- encoding: utf-8 -*- 
#############################################################################
#    Module Writen to Odoo 10 Community Edition
#    All Rights Reserved to Experts SA de CV or Experts SAS
#############################################################################
#
#    Coded by: Marco Hernández (marco.hernandez@experts.com.mx)
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
    "name" : "cqn_sale_lots",
    "version" : "1.0",
    "author" : "experts.com.mx",
    "category" : "Sale",
    "description" : """
        Módulo personalizado para el manejo de ventas con lotes en CQN. \n
            * Éste módulo le permite agregar notas por producto en la línea de venta, además podrá agregar una nota general para almacén, la cual podrá leer el almacenista.
            * Por medio de un botón podrá ver los lotes correspondientes al producto por línea de venta, así como su disponibilidad y fecha de caducidad.
        Si tiene dudas, quiere reportar algún error o mejora póngase en contacto con nosotros: info@experts.com.mx
        """,
    'website': 'http://experts.com.mx',
    "license" : "AGPL-3",
    "depends" : ['base','sale'],
    "demo" : [],
    "data" : [
        'views/sale_order_view.xml',
        'views/stock_view.xml',
        'wizard/sale_order_lots_wizard_view.xml',
            ],
    "installable" : True,
    "active" : False,
}
 
