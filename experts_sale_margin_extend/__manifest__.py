# -*- encoding: utf-8 -*-
#############################################################################
#    Module Writen to Odoo 10 Community Edition
#    All Rights Reserved to Experts SA de CV or Experts SAS
#############################################################################
#
#    Coded by: Mauricio Ruiz (mauricio.ruiz@experts.com.mx)
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
    "name" : 'Margin extend',
    "version" : '0.1',
    "author" : 'experts.com.mx',
    "category" : 'Modules',
    "website" : "",
    "description" : """
        Módulo que extiende la funcionalidad de  Odoo respecto al margen en las órdenes de ventas.
            * Agrega un permiso para permitir a ciertos usuarios ver o no el margen de las ventas.
            * Funciona tanto como para la vista "lista" como para la vista "formulario"
            * Agrega una pestaña en la configuración de la compañía para especificar las configuraciones siguientes:
              - Restringir venta si se excede el porcentaje permitido
              - Porcentaje permitido de margen al realizar la venta
              - Criterio sobre el cual se aplicará el porcentaje (Total de venta o por linea de venta)
            * Agrega un permiso para permitir a ciertos usuarios ver o no el margen y el costo total en las facturas en vista "lista".

        Si tiene dudas, quiere reportar algún error o mejora póngase en contacto con nosotros: info@experts.com.mx
    """,
    "init_xml" : [],
    "depends" : ['experts_groups','sale_margin'],
    "data" : ['views/sale_order_view.xml','security/groups.xml','views/res_company_view.xml','views/invoice_view.xml'],
    "demo_xml":[],
    "test":[],
    "installable": True,
    "images": [],
    "auto_install": False,
}
