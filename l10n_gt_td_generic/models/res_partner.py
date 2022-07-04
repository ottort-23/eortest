# -*- coding: utf-8 -*-

import requests
from xml.etree.ElementTree import fromstring, ElementTree

from odoo import fields, api, models, _
from odoo.exceptions import ValidationError
from odoo.tools import config


class Partner(models.Model):
    _inherit = 'res.partner'

    legal_name = fields.Char(string="Razón Social")
    vat = fields.Char(string="NIT", default='CF')

    @api.constrains('vat')
    def _check_vat_unique(self):
        for record in self:
            duplicate_nit = record.env.company.duplicate_nit

            if record.parent_id or not record.vat or record.vat == 'CF':
                continue
            test_condition = (config['test_enable'] and
                              not self.env.context.get('test_vat'))
            if test_condition:
                continue
            results = self.env['res.partner'].search_count([
                ('parent_id', '=', False),
                ('vat', '=', record.vat),
                ('legal_name', '=', record.legal_name),
                ('id', '!=', record.id),
                ('company_id', '=', record.env.company.id),
                ('country_id', '=', record.country_id.id)
            ])
            if results and not duplicate_nit:
                raise ValidationError(_(
                    "El número de NIT %s ya existe.") % record.vat)

    @api.model
    def search_legal_name_by_nit(self, nit, name):
        """Consulta de razón social por medio de NIT ingresado.
                Verificación de la razón social en el servicio web de la SAT.
            """
        ulr = 'https://www.ingface.net/ServiciosIngface/ingfaceWsServices'
        headers = {'content-type': 'text/xml'}
        data = """
                   <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ser="http://services.ws.ingface.com/">
                   <soapenv:Header/>
                   <soapenv:Body>
                       <ser:nitContribuyentes>
                           <!--Optional:-->
                               <usuario>CONSUMO_NIT</usuario>
                           <!--Optional:-->
                           <clave>58B45D8740C791420C53A49FFC924A1B58B45D8740C791420C53A49FFC924A1B</clave>
           """

        data += """<nit>""" + nit.strip().replace("-", "") + """</nit>"""
        data += """</ser:nitContribuyentes>"""
        data += """</soapenv:Body>"""
        resp = requests.post(url=ulr, data=data, headers=headers)

        tree = ElementTree(fromstring(resp.text))
        root = tree.getroot()
        datadict = {}
        elements = [elem for body in root for item in body for response in item for elem in response]
        for elem in elements:
            datadict[elem.tag] = elem.text

        legal_name = datadict.get('nombre')
        if 'Nit no valido' == legal_name:
            raise ValidationError(legal_name)
        elif not legal_name:
            legal_name = name
        return legal_name

    @api.onchange('vat')
    def _onchange_vat(self):
        if not self.vat == 'CF' and self.l10n_latam_identification_type_id.is_vat:
            if self.vat:
                legal_name = self.search_legal_name_by_nit(self.vat, self.name)
                self.legal_name = legal_name
            else:
                raise ValidationError('Valor ingresado para NIT no es válido. Ingréselo un NIT por favor.')

    def write(self, vals):
        """Herencia al método genérico write para llenar el campo razón social
            en los contactos que no tienen razón social ingresada"""
        for record in self:
            if not record.legal_name and not vals.get('legal_name', False):
                vals['legal_name'] = record.browse(record.parent_id.id).legal_name or record.browse(record.parent_id.id).name \
                    if record.parent_id else record.name
        res = super(Partner, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        """Actualización del 15.07.2021
            Herencia realizada para mejorar el método create,
             para asignarle la razón social de la empresa padre si tuviere contacto padre,
             caso contrario colocar el nombre ingresado como razón social.
        """
        if not vals.get('legal_name', False):
            vals['legal_name'] = self.browse(vals['parent_id']).legal_name \
                                 if vals.get('parent_id', False) else vals.get('name', 'Ingresar una razón social.')
        res = super(Partner, self).create(vals)
        return res
