# -*- coding: utf-8 -*-

from odoo import fields, models


class SalesDiscountLimit(models.Model):
    """Configuration for Set Sale Discount Limit."""

    _name = "sales.discount.limit"
    _description = "Configuration for Set Sale Discount Limit"

    _sql_constraints = [
        ('discount', 'check(discount >= 1 and discount <= 100)',
         'Discount should be between 1 to 100 percentage.'),
        ('group_id_uniq', 'unique(group_id)',
            'Group already exists!'),
    ]

    group_id = fields.Many2one(
        'res.groups', "Group", domain=lambda self: [
            ('category_id.id', '=',
                self.env.ref('base.module_category_sales_management').id)])
    discount = fields.Float("Discount (%)",
                            digits='Discount', default=10.0)
