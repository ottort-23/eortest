# -*- coding: utf-8 -*-

# Created on 2018-11-01
# author: 广州尚鹏，https://www.sunpop.cn
# email: 300883@qq.com
# resource of Sunpop
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# Odoo在线中文用户手册（长期更新）
# https://www.sunpop.cn/documentation/user/10.0/zh_CN/index.html

# Odoo10离线中文用户手册下载
# https://www.sunpop.cn/odoo10_user_manual_document_offline/
# Odoo10离线开发手册下载-含python教程，jquery参考，Jinja2模板，PostgresSQL参考（odoo开发必备）
# https://www.sunpop.cn/odoo10_developer_document_offline/
# description:
from odoo import models, fields, api, exceptions, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('uom_id')
    def _onchange_uom_weight(self):
        # 取计重的单位
        weight_uom_id = self.product_tmpl_id._get_weight_uom_id_from_ir_config_parameter()

        for product in self:
            # 如果默认单位是重量，则计重亦用1
            # 自动转换单位
            if product.uom_id and product.uom_id.category_id == weight_uom_id.category_id:
                product.weight = product.uom_id._compute_quantity(1, weight_uom_id)
