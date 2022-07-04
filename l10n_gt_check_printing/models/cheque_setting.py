# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class ChequeSetting(models.Model):
    _name = 'cheque.setting'
    _description = 'Configuracion de cheque'

    name = fields.Char('Nombre', required="1")
    font_size_check = fields.Float('Tamaño de Letra Cheque', default="18", required="1")
    font_size = fields.Float('Tamaño de Letra Diario / Asiento', default="15", required="1")
    color = fields.Char('Color', default="#000", required="1")
    # set_default = fields.Boolean('Default Template', copy=False) company_id = fields.Many2one('res.company',
    # string='Company', default=lambda self:self.env.user.company_id.id, required="1")

    is_partner = fields.Boolean('Es empresa?', default=True)
    is_partner_bold = fields.Boolean('Letra en Negrita')
    partner_text = fields.Selection([('prefix', 'Prefix'), ('suffix', 'Suffix')], string='Título a Contacto')
    partner_m_top = fields.Float('Desde Arriba empresa', default=130)
    partner_m_left = fields.Float('Desde Izquierda', default=75)

    is_date = fields.Boolean('Es fecha', default=True)
    date_formate = fields.Selection([('dd_mm', 'DD MM'), ('mm_dd', 'MM DD')], string='Formato Fecha', default='dd_mm')
    year_formate = fields.Selection([('yy', 'YY'), ('yyyy', 'YYYY')], string='Formato Año', default='yy')
    date_m_top = fields.Float('Desde Arriba fecha', default=101.24)
    gt_left = fields.Float('País', default=75)
    f_d_m_left = fields.Float('Primer Dígito', default=150)
    s_d_m_left = fields.Float('Segundo Dígito', default=160)
    t_d_m_left = fields.Float('Tercer Dígito', default=190)
    fo_d_m_left = fields.Float('Cuatro Dígito', default=200)
    fi_d_m_left = fields.Float('Quinto Dígito', default=225)
    si_d_m_left = fields.Float('Sexto Dígito', default=235)
    se_d_m_left = fields.Float('Séptimo Dígito', default=245)
    e_d_m_left = fields.Float('Octavo Dígito', default=255)
    
    date_seprator = fields.Char('Separador')

    is_amount = fields.Boolean('Es monto', default=True)
    amt_m_top = fields.Float('Desde Arriba', default=101.24)
    amt_m_left = fields.Float('Desde Izquierda', default=650)
    is_star = fields.Boolean('Imprimir Asteríco 1',
                             help="Si es seleccionado imprimirá 3 asteríscos antes y después del monto.", default=True)

    is_currency = fields.Boolean('Imprimir Moneda')

    is_amount_word = fields.Boolean('Imprimir', default=True)
    is_word_bold = fields.Boolean('Letra en Negrita')
    word_in_f_line = fields.Float('Palabras en primera línea', default=5,
                                  help="Cuántas palabras desea imprimir en la primera línea, "
                                       "El resto ira en la segunga línea")
    amt_w_m_top = fields.Float('Desde Arriba antes', default=158.76)
    amt_w_m_left = fields.Float('Desde Izquierdo antes', default=70)
    is_star_word = fields.Boolean('Imprimir Asteríco 2',
                                  help="Si es seleccionado imprimirá 3 asteríscos antes y después del monto.",
                                  default=True)

    amt_w_s_m_top = fields.Float('Desde Arriba después', default=185)
    amt_w_s_m_left = fields.Float('Desde Izquierdo después', default=70)

    is_company = fields.Boolean('Impimir is company')
    c_margin_top = fields.Float('Desde Arriba margen top', default=380)
    c_margin_left = fields.Float('Desde c margin Izquierda', default=75)

    print_journal = fields.Boolean('Imprimir print journal')
    journal_margin_top = fields.Float('Desde Arriba journal margin', default=300)
    journal_margin_left = fields.Float('Desde journal margin left', default=10)

    is_stub = fields.Boolean('Imprimir is stub')
    stub_margin_top = fields.Float('Desde Arriba Talon', default=700)
    stub_margin_left = fields.Float('Desde margin left', default=10)

    is_cheque_no = fields.Boolean('Imprimir is cheque')
    cheque_margin_top = fields.Float('Desde Arriba Top', default=408.46)
    cheque_margin_left = fields.Float('Desde Izquierda margin left', default=75)

    is_free_one = fields.Boolean('Imprimir free one')
    f_one_margin_top = fields.Float('Desde Arriba Margen top', default=758.46)
    f_one_margin_left = fields.Float('Desde Izquierda one margin left', default=75)

    is_communication = fields.Boolean('Imprimir communication')
    f_two_margin_top = fields.Float('Desde Arriba margen top', default=730.00)
    f_two_margin_left = fields.Float('Desde Izquierda margin left', default=75)

    is_non_negotiable = fields.Boolean('Imprimir non negotiable')
    non_n_margin_top = fields.Float('Desde Arriba non top', default=213)
    non_n_margin_left = fields.Float('Desde Izquierda margin left', default=75)

    is_acc_pay = fields.Boolean('Imprimir A/C PAY', default=True)
    acc_pay_m_top = fields.Float('Desde Arriba pay m top', default=50)
    acc_pay_m_left = fields.Float('Desde Izquierda pay m left', default=50)
    
    is_f_line_sig = fields.Boolean('Imprimir f line sig')
    f_sig_m_top = fields.Float('Desde Arriba f sig top', default=960)
    f_sig_m_left = fields.Float('Desde Izquierda f sig left', default=100)
    
    is_s_line_sig = fields.Boolean('Imprimir s sig')
    s_sig_m_top = fields.Float('Desde Arriba s sig top', default=960)
    s_sig_m_left = fields.Float('Desde Izquierda s sig left', default=530)

    # @api.constrains('set_default', 'company_id') def _check_description(self): for line in self: if
    # line.set_default: line_ids = self.env['cheque.setting'].search([('set_default','=',True),('company_id','=',
    # line.company_id.id)]) if len(line_ids) > 1: raise ValidationError("One Company have one default cheque template")

# vim:expandtab:smartindent:tabstop=4:4softtabstop=4:shiftwidth=4:
