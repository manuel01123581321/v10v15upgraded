from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    brand_id = fields.Many2one('product.brand', 'Product Brand', readonly=True)

    def _select(self):
        return super(SaleReport, self)._select() + ", t.brand_id AS brand_id"

    def _group_by(self):
        return super(SaleReport, self)._group_by() + ", t.brand_id"
