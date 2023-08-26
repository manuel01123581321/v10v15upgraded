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
#####################################################################################
{
    "name" : "cqn_product_extend",
    "version" : "1.0",
    "author" : "experts.com.mx",
    "category" : "Product",
    "description" : """
        Mejoras al módulo de producto\n
            - Se agrega el campo temperatura a los productos en la pestaña inventario
            - No se puede validar un picking de entrada si las lineas de estos no tienen el campo temperatura

        Si tiene dudas, quiere reportar algún error o mejora póngase en contacto con nosotros: info@experts.com.mx
    """,
    'website': 'http://experts.com.mx',
    "license" : "AGPL-3",
    "depends" : ['base','stock','product','sale','stock_available_unreserved'],
    "demo" : [],
    "data" : [
        'views/product_view.xml',
        'views/stock_view.xml',
        "security/ir.model.access.csv",
            ],
    "installable" : True,
    "active" : False,
}
