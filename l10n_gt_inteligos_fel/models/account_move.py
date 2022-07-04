# -*- coding: utf-8 -*-

from datetime import datetime
from pytz import timezone, UTC
from dateutil.parser import parse
from math import trunc
from uuid import uuid4

import hashlib
import time
import logging
import requests

from ..providers.infile import InfileFel, emisor, receptor
from ..providers.digifact import DigifactFel, DigifactEmisor, DigifactReceptor
from ..providers.contap import ContapFel, ContapEmisor, ContapReceptor
from ..providers.megaPrint import MegaPrintFel, MegaPrintEmisor, MegaPrintReceptor
from ..providers.ecofacturas import EcofacturaFel, EcofacturaEmisor, EcofacturaReceptor

from odoo import models, fields, api, tools
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class FelLog(models.Model):
    _name = "account.move.fel_log"
    _description = 'Logs FEL'

    response = fields.Char("Respuesta", required=True, readonly=True)
    type = fields.Selection(
        [
            ("S", "Satisfactorio"),
            ("E", "Error")
        ], required=True, readonly=True
    )
    timestamp = fields.Datetime("Fecha", required=True, readonly=True)
    error_msg = fields.Char("Mensaje Error", readonly=True)
    source = fields.Char("Fuente", readonly=True)
    category = fields.Char("Categoria", readonly=True)
    numeral = fields.Char("Numeral", readonly=True)
    validation = fields.Char("Validacion", readonly=True)
    account_move_id = fields.Many2one("account.move", required=True, readonly=True)
    contingency_id = fields.Many2one("account.fel_contingency", readonly=True)


class fel_contingency(models.Model):
    _name = "account.fel_contingency"
    _description = 'Contingencias FEL'

    date_start = fields.Datetime("Fecha y Hora Inicio", required=True, readonly=True, copy=False)
    date_end = fields.Datetime("Fecha y Hora Fin", readonly=True, copy=False)
    location = fields.Char("Numero Establecimiento", readonly=True, copy=False)
    source = fields.Char("Motivo", required=True, copy=False)
    documents_qty = fields.Integer("Cantidad Documentos", copy=False)
    logs = fields.One2many("account.move.fel_log", "contingency_id", "Bitácora FEL", readonly=True, copy=False)
    move_ids = fields.One2many(comodel_name="account.move", inverse_name="contingency_id", string="Documentos")

    @api.depends('move_ids')
    def compute_docs_qty(self):
        for record in self:
            record.documents_qty = len(record.move_ids)


class AccountMoveReversalInherited(models.TransientModel):
    _inherit = "account.move.reversal"

    @api.model
    def _doc_type_domain(self):
        return [
            ('id', 'in', (self.env.ref('l10n_gt_td_generic.dc_ncre').id, self.env.ref('l10n_gt_td_generic.dc_ndeb').id,
                          self.env.ref('l10n_gt_td_generic.dc_nabn').id))
        ]

    dte_to_note_id = fields.Many2one("account.move", string="DTE para hacer Nota")
    """Actualizacion 11.05.2021
        Mejora para agregar tipo de documento rectificativo"""
    dte_doc_type = fields.Many2one(
        comodel_name='l10n_latam.document.type',
        required=True, string='Tipo Documento', copy=False,
        domain=_doc_type_domain
    )
    """----------Fin de atualizacion 11.05.2021-----------"""

    def _prepare_default_reversal(self, move):
        res = super(AccountMoveReversalInherited, self)._prepare_default_reversal(move)
        res['dte_to_note_id'] = self.dte_to_note_id.id or move.id
        res['reason_note'] = self.reason or " "
        res['pos_inv'] = False
        """Actualizacion 11.05.2021
            Mejora para agregar tipo de documento rectificativo"""
        res['invoice_doc_type'] = self.dte_doc_type.id
        """----------Fin de atualizacion 11.05.2021-----------"""
        return res


class AccountMoveInherited(models.Model):
    _inherit = "account.move"
    _name = "account.move"

    def compute_total_amount(self):
        for record in self:
            total = sum([line.line_total for line in record.invoice_line_ids])
            record.amount = total

    amount = fields.Monetary(compute="compute_total_amount", string="Suma total")
    state = fields.Selection(
        selection_add=[
            ('contingency', 'Contingencia')
        ], ondelete={'contingency': 'cascade'}, string='Estado',
    )
    pos_inv = fields.Boolean(default=False, store=True, string="Factura POS", copy=False)
    contingency_id = fields.Many2one("account.fel_contingency", readonly=True, copy=False)
    key_identifier = fields.Char("Identificador Único",
                                 help="Este campo puede ser alfanumérico de 32 caracteres, "
                                      "sirve como identificador único de los documentos "
                                      "eletrónicos del emisor, para evitar duplicidad de los mismos.",
                                 copy=False)
    validate_internal_reference = fields.Selection(
        selection=[('VALIDAR', 'VALIDAR'), ('NO_VALIDAR', 'NO VALIDAR')],
        default="VALIDAR",
        help="Este campo puede ser usado para momentos de contingencia en donde sea necesario emitir un DTE, "
             "aunque no se tenga acceso a internet. "
             "Lo cual hará que DIGIFACT almacene este documento para ser emitido en un máximo de 5 días despues.",
        copy=False,
        string="Validar Documento por Contingencia"
    )

    doc_xml_generated = fields.Char('XML Generado', copy=False)
    certify_xml = fields.Char('XML Certificado', copy=False)
    signed_xml = fields.Char('XML Firmado', copy=False)
    fel_uuid = fields.Char("UUID", readonly=True, copy=False)
    fel_serie = fields.Char("Serie FEL", readonly=True, copy=False)
    fel_number = fields.Char("Numero FEL", readonly=True, copy=False)
    fel_date = fields.Char("Fecha FEL", readonly=True, copy=False)
    fel_num_acceso = fields.Char("Numero Acceso FEL", readonly=True, copy=False)
    fel_logs = fields.One2many("account.move.fel_log", "account_move_id", "Bitácora FEL",
                               readonly=True, copy=False, tracking=3)

    ancient_regime = fields.Boolean(string="Régimen Antiguo", default=False, copy=False)
    date_ancient_regime = fields.Char(store=True, copy=False, string="Fecha de Régimen Antiguo")
    series_ancient_regime = fields.Char(store=True, copy=False, string="Serie de Régimen Antiguo")
    doc_ancient_regime = fields.Char(store=True, copy=False, string="# Doc Régimen Antiguo")
    uuid_ancient_regime = fields.Char(store=True, copy=False, string="# Autorización de Régimen Antiguo")

    reason_note = fields.Char("Motivo Ajuste", default=' ', copy=False)
    dte_to_note_id = fields.Many2one("account.move", string="DTE para Nota", copy=False)

    """Actualización del 28.10.2021 para eliminar funcionamiento de campos dobres paras datos FEL"""
    date_dte_to_refund = fields.Char(related="dte_to_note_id.fel_date", string="Fecha de DTE para NCRE")
    series_dte_to_refund = fields.Char(related="dte_to_note_id.fel_serie", string="Serie de DTE para NCRE")
    number_dte_to_refund = fields.Char(related="dte_to_note_id.fel_number", string="Número de DTE para NCRE")
    uuid_dte_to_refund = fields.Char(related="dte_to_note_id.fel_uuid", string="UUID de DTE para NCRE")

    doc_xml_cancel_generated = fields.Char('XML Cancelación Generado', copy=False)
    certify_cancel_xml = fields.Char('XML Cancelación Certificado', copy=False)
    signed_cancel_xml = fields.Char('XML Cancelación Firmado', copy=False)
    fel_uuid_cancel = fields.Char("UUID Anulacion", readonly=True, copy=False)
    fel_series_cancel = fields.Char("Serie FEL Anulacion", readonly=True, copy=False)
    fel_number_cancel = fields.Char("Numero FEL Anulacion", readonly=True, copy=False)
    fel_date_cancel = fields.Char("Fecha FEL Anulacion", readonly=True, copy=False)
    fel_num_acceso_cancel = fields.Char("Numero Acceso FEL Anulacion", readonly=True, copy=False)
    """Actualización del 28.10.2021 para eliminar funcionamiento de campos dobles paras datos FEL"""

    def truncate(self, number, decimals=0):
        factor = 10.0 ** decimals
        return trunc(number * factor) / factor

    def create_message_data_fel(self, response_fel):
        """Actualización del 11/05/2021
            Mejora para obtención de tipo de documento para chatter."""
        dte_type = self._get_sequence().l10n_latam_document_type_id.doc_code_prefix
        """-----------Fin de actualizacion del 11/05/2021----------------"""

        if dte_type.strip() not in ['NCRE', 'NDEB']:
            doc = 'Factura'
        elif dte_type.strip() == 'NDEB':
            doc = 'Nota de Débito'
        else:
            doc = 'Nota de Crédito'

        if self.state == 'posted':
            doc = 'Anulación ' + doc

        display_msg = """<b>Datos """ + doc + """ FEL:</b> 
                         <br/> 
                          <ul>
                              <li>UUID: """ + response_fel["uuid"] + """</li>
                              <li>Serie FEL: """ + response_fel["serie"] + """</li>
                              <li>Numero FEL: """ + str(response_fel["numero"]) + """</li>
                              <li>Fecha FEL: """ + response_fel["fecha"] + """</li>
                              <li>Numero Acceso FEL: </li>
                          </ul> 
                          <br/>"""
        if self.state == 'draft' and self.company_id.fel_provider == 'IN':
            display_msg += """<a href='https://report.feel.com.gt/ingfacereport/ingfacereport_documento?uuid=""" + \
                           response_fel[
                               "uuid"] + """' target='_blank'>Aquí puede visualizar el formato INFILE del documento emitido.</a>"""
        followers = self.message_partner_ids.ids
        odoobot = self.env.ref('base.partner_root')
        self.message_post(body=display_msg, message_type='notification', subject="Datos FEL",
                          partner_ids=followers, starred=True, author_id=odoobot.id)

    def manage_contingency(self, move, response_fel):
        if move.state == 'draft':
            move.state = 'contingency'
            instance_contingency = self.env['account.fel_contingency']
            contingency = instance_contingency.search([('date_end', '=', False)])

            if not contingency:
                """Pensar sobre esto"""
                loc = ''
                contingency_values = {
                    'date_start': fields.Datetime.now(), 'location': loc,
                    'source': response_fel["descripcion"],
                    'move_ids': [(1, move.id, {'name': move.name})]
                }
                instance_contingency.create(contingency_values)
            elif contingency and contingency.filtered(lambda c: c['move_ids'] not in move.id):
                contingency.move_ids += [(1, move.id, {'name': move.name})]

    def void_contingency(self, contingency):
        for move in contingency.move_ids:
            if move.state == 'contingency':
                move.action_post()

    def response_dte_fel(self, response_fel, xml_generated, certify_xml, signed_xml, fel_uuid, fel_date,
                         fel_series, fel_number, account_move_id):
        for move in self:
            result = response_fel.get("resultado", False)
            instance_contingency = self.env['account.fel_contingency']
            """Actualizaciones del 09.09.2021
                Mejoras para manejar errores luego de certificaciones FEL
            """
            instance_log = self.env['account.move.fel_log']
            gt = timezone('America/Guatemala')
            utc_dt = datetime.now(tz=UTC).astimezone(gt)
            date = utc_dt.strftime('%Y-%m-%d %H:%M:%S')
            """Actualizaciones del 09.09.2021
                Mejoras para manejar errores luego de certificaciones FEL
            """
            if result:
                move[xml_generated] = response_fel["xml_plano"]
                move[certify_xml] = response_fel["xml_certificado"]
                move[signed_xml] = response_fel["xml_firmado"]
                move[fel_uuid] = response_fel["uuid"]
                move[fel_date] = response_fel["fecha"]
                move[fel_series] = response_fel["serie"]
                move[fel_number] = str(response_fel["numero"])
                """Actualizaciones del 09.09.2021
                    Mejoras para manejar errores luego de certificaciones FEL
                """
                try:
                    move.create_message_data_fel(response_fel)
                except Exception as e:
                    obj_log = {
                        'response': tools.ustr(e),
                        'type': 'E', 'timestamp': date,
                        'error_msg': tools.ustr(e),
                        'source': 'Odoo-Certificador',
                        'category': 'ERROR AL OBTENER REPORTE FEL',
                        'numeral': '#',
                        'validation': '',
                        'account_move_id': account_move_id
                    }
                    instance_log.create(obj_log)
                    """Actualizaciones del 09.09.2021
                        Mejoras para manejar errores luego de certificaciones FEL
                    """

                #  ACTUALIZACION UTIL PARA CONTINGENCIAS
                if move.state == 'contingency':
                    move.state = 'draft'

                    contingency = instance_contingency \
                        .search([('date_end', '=', False), ('move_ids', 'in', move.id)])
                    if contingency:
                        contingency.date_end = fields.Datetime.now()

                    #  AQUI LLAMAR AL METODO PARA VACIAR LA CONTINGENCIA
                    #  REVISAR DETENIDAMENTE EL PROCESO, YA QUE TIENE FALLOS
                    move.void_contingency(contingency)
                    #  AQUI LLAMAR AL METODO PARA VACIAR LA CONTINGENCIA
                #  ACTUALIZACION UTIL PARA CONTINGENCIAS

                if response_fel.get('pdf', False):
                    self.env['ir.attachment'].create({
                        'name': "PDF de emisión",
                        'type': 'binary',
                        'datas': response_fel['pdf'],
                        'store_fname': "PDF",
                        'res_model': move._name,
                        'res_id': move.id,
                        'mimetype': 'application/x-pdf'
                    })
                return True

            else:
                move[xml_generated] = response_fel["xml_plano"]
                if response_fel.get('descripcion_errores', False):  # Espera una lista
                    self.env.user.notify_danger(message='No fue posible emitir el documento, '
                                                        'tómate un tiempo para revisar en la sección de abajo ---> '
                                                        '***Datos FEL*** lo que ha ocurrido.')
                    for error_fel in response_fel['descripcion_errores']:
                        obj_log = {
                            'response': response_fel["descripcion"],
                            'type': 'E', 'timestamp': date,
                            'error_msg': error_fel["mensaje_error"],
                            'source': error_fel["fuente"],
                            'category': error_fel["categoria"],
                            'numeral': error_fel["numeral"],
                            'validation': error_fel["validacion"],
                            'account_move_id': account_move_id
                        }

                        #  ACTUALIZACION UTIL PARA CONTINGENCIAS AUN FALTA
                        #  REVISAR
                        log = instance_log.create(obj_log)
                        contingency = instance_contingency.search([('date_end', '=', False)])
                        if contingency and response_fel.get('access_number'):
                            contingency.logs += [(1, log.id, {'error_msg': log.error_msg})]
                    if response_fel.get('access_number'):
                        move.manage_contingency(move, response_fel)
                        move[fel_uuid] = response_fel["access_number"]

                    elif move.pos_inv:
                        raise ValidationError(
                            'La emisión de DTE no pudo ser realizada por errores ocurridos. '
                            'Favor revisar los registros de errores FEL '
                            'ERROR: ' +
                            response_fel['descripcion_errores'][0]["mensaje_error"] +
                            ' XML: ' + response_fel.get('xml_plano')
                        )
                    #  ACTUALIZACION UTIL PARA CONTINGENCIAS AUN FALTA
                    return False
                else:
                    #  ACTUALIZACION UTIL PARA CONTINGENCIAS AUN FALTA
                    if response_fel.get('access_number'):
                        move.manage_contingency(move, response_fel.get('sign_response'))
                    else:
                        raise ValidationError(
                            response_fel.get('descripcion', '') + ' ' +
                            str(response_fel.get('sign_response', '')) +
                            ' XML: ' + response_fel.get('xml_plano', '')
                        )
                #  ACTUALIZACION UTIL PARA CONTINGENCIAS

    def data_notes(self, doc):
        note = ''
        dte_id = self.dte_to_note_id
        date_dte = self.date_dte_to_refund
        uuid_dte = self.uuid_dte_to_refund
        series_dte = self.series_dte_to_refund
        doc_dte = self.number_dte_to_refund
        if doc == 'NCRE':
            note = 'Crédito'
        elif doc == 'NDEB':
            note = 'Débito'
        if self.ancient_regime:
            data_to_ncre = [self.series_ancient_regime, self.uuid_ancient_regime, self.date_ancient_regime]
            for data in data_to_ncre:
                if not data:
                    raise ValidationError('No puedes hacer la Nota de ' + note + ' para el régimen '
                                                                                 'antiguo, pues hay campos '
                                                                                 'obligatorios sin datos.')
            fel_date = parse(self.date_ancient_regime).strftime("%Y-%m-%d")
            uuid = self.uuid_ancient_regime
            series = self.series_ancient_regime
            doc_dte = self.doc_ancient_regime
            return {
                'fel_date': fel_date,
                'uuid': uuid,
                'series': series,
                'doc_dte': doc_dte
            }
        else:
            if dte_id:
                fel_date = parse(date_dte).strftime("%Y-%m-%d")
                return {
                    'fel_date': fel_date,
                    'uuid': uuid_dte,
                    'series': series_dte,
                    'doc_dte': doc_dte
                }
            else:
                raise ValidationError('No existe un documento FEL para el que '
                                      'deseas hacer una Nota de ' + note + '.')

    def tax(self, taxable_unit_code, taxable_amount, tax_amount):
        return {
            'taxable_unit_code': taxable_unit_code,
            'taxable_amount': taxable_amount,
            'tax_amount': tax_amount
        }

    def set_key_identifier(self):
        if self.company_id.fel_provider == "MP":
            identifier = "-".join(str(uuid4()).split("-")).upper()
        elif self.company_id.fel_provider == "ECO":
            identifier = self.company_id.get_doc_identifier()
        else:
            hash_sha = hashlib.sha1()
            hash_sha.update(str(time.time()).encode('utf-8'))
            identifier = hash_sha.hexdigest()[:32]
        return identifier

    def examine_values(self, values, factor):
        values_evaluated = {}
        for key, val in values.items():
            if val:
                values_evaluated[key] = val.strip().replace("&", "&amp;").replace("'", "&apos;"). \
                    replace(">", "&gt;").replace('"', "&quot;").replace('ñ', "&#241;").replace('Ñ', "&#209;") \
                    .replace('á', "&#225;").replace('é', "&#233;").replace('í', "&#237;") \
                    .replace('ó', "&#243;").replace('ú', "&#250;").replace('Á', "&#193;") \
                    .replace('É', "&#201;").replace('Í', "&#205;") \
                    .replace('Ó', "&#211;").replace('Ú', "&#218;") \
                    if key.upper() != 'NIT' else val.replace("-", "")
            else:
                raise ValidationError('Falta llenar campo ' + key + ' en ' + factor)
        return values_evaluated

    def dte_fel(self):
        for move in self:
            _logger.info("ESTAS DENTRO DE FEL!")
            instance_company = move.company_id
            instance_partner = move.partner_id

            if instance_company.fel_provider == 'IN':
                provider = InfileFel
                emisor_fel = emisor
                receptor_fel = receptor
            elif instance_company.fel_provider == 'DI':
                provider = DigifactFel
                emisor_fel = DigifactEmisor
                receptor_fel = DigifactReceptor
            elif instance_company.fel_provider == 'CO':
                provider = ContapFel
                emisor_fel = ContapEmisor
                receptor_fel = ContapReceptor
            elif instance_company.fel_provider == "MP":
                provider = MegaPrintFel
                emisor_fel = MegaPrintEmisor
                receptor_fel = MegaPrintReceptor
            elif instance_company.fel_provider == "ECO":
                provider = EcofacturaFel
                emisor_fel = EcofacturaEmisor
                receptor_fel = EcofacturaReceptor
            else:
                raise ValidationError('No ha seleccionado a ningún proveedor para la emisión FEL. '
                                      'Debe ser configurado en la compañía emisora. '
                                      'Por favor hágalo o comuníquese con administración.')

            # Metodos principales de librerias FEL según cada proveedor
            certify_fel_dte = provider.fel_dte()
            emisor_fel = emisor_fel.emisor()
            receptor_fel = receptor_fel.receptor()

            # Variables para emisor y receptor
            factor = 'compañía'
            establishment_code = instance_company.establishment_number
            street = False
            zip_code = False
            city = False
            state = False
            country = False
            name = False
            receptor_name = False
            receptor_street = False
            receptor_city = False
            receptor_state = False
            receptor_country = False
            receptor_zip = False
            receptor_email = False
            if move.pos_inv:
                po_order = self.env['pos.order'].search([('account_move', '=', move.id)], limit=1)
                if po_order:
                    instance_config_po = po_order.session_id.config_id
                    street = instance_config_po.street
                    zip_code = instance_config_po.zip_code
                    city = instance_config_po.county_name
                    state = instance_config_po.state_id.name
                    country = instance_config_po.country_id.code
                    name = instance_config_po.name
                    establishment_code = str(instance_config_po.establishment_number)
                    factor = 'punto de venta'
                    receptor_name = self.validate_nit(instance_partner.vat) \
                        if instance_partner.vat != 'CF' else instance_partner.legal_name or instance_partner.name
                    instance_partner.legal_name = receptor_name
                    receptor_street = instance_partner.street or 'Guatemala'
                    """Mejora 16/03/2021 tras cambios al agregar TD Municipios"""
                    # receptor_city = instance_partner.county_id.name if instance_partner.county_id else ' '
                    receptor_city = instance_partner.city if instance_partner.city else ' '
                    """Mejora 16/03/2021 tras cambios al agregar TD Municipios"""
                    receptor_state = instance_partner.state_id.name or ' '
                    receptor_country = instance_partner.country_id.code or 'GT'
                    receptor_zip = instance_partner.zip or '00000'
                    receptor_email = instance_partner.email or ' '
            else:
                street = instance_company.street
                zip_code = instance_company.zip
                city = instance_company.county_id.name
                state = instance_company.state_id.name
                country = instance_company.country_id.code
                name = instance_company.name
                receptor_name = instance_partner.legal_name.strip()
                receptor_email = instance_partner.email
                if not instance_company.fel_provider == "MP":
                    receptor_email = instance_partner.email or ' '
                """Actualización 28.06.2021
                    Mejora para agregar lógica de configuración para el ingreso de direcciones FEL.
                    Obligatoria o no, en dependencia de la configuración.
                """
                if not instance_company.mandatory_address_fel:
                    receptor_street = instance_partner.street or 'Guatemala'
                    """Mejora 16/03/2021 tras cambios al agregar TD Municipios"""
                    receptor_city = instance_partner.county_id.name if instance_partner.county_id else 'Guatemala'
                    """Mejora 16/03/2021 tras cambios al agregar TD Municipios"""
                    receptor_state = instance_partner.state_id.name or 'Guatemala'
                    receptor_country = instance_partner.country_id.code or 'GT'
                    receptor_zip = instance_partner.zip or '00000'
                else:
                    receptor_street = instance_partner.street
                    """Mejora 16/03/2021 tras cambios al agregar TD Municipios"""
                    receptor_city = instance_partner.county_id.name if instance_partner.county_id else False
                    """Mejora 16/03/2021 tras cambios al agregar TD Municipios"""
                    receptor_state = instance_partner.state_id.name
                    receptor_country = instance_partner.country_id.code
                    receptor_zip = instance_partner.zip
                """------Fin Actualización 28.06.2021
                    Mejora para agregar lógica de configuración para el ingreso de direcciones FEL.-------
                """

            # Datos emisor
            direction_values_emisor = {
                'Calle': street, 'Código Postal': zip_code,
                'Ciudad': city, 'Departamento': state,
                'País': country
            }
            vde = self.examine_values(direction_values_emisor, factor)
            if instance_company.fel_provider != "ECO":
                emisor_fel.set_direccion(vde['Calle'], vde['Código Postal'], vde['Ciudad'], vde['Departamento'],
                                         vde['País'])
            data_values_emisor = {
                'Fel Iva': instance_company.fel_iva, 'Correo': instance_company.email,
                'Nit': instance_company.vat, 'Nombre Comercial': name,
                'Razón Social': instance_company.legal_name
            }
            dve = self.examine_values(data_values_emisor, factor)
            emisor_fel.set_datos_emisor(dve['Fel Iva'], establishment_code, dve['Correo'],
                                        dve['Nit'], dve['Nombre Comercial'], dve['Razón Social'])
            certify_fel_dte.set_datos_emisor(emisor_fel)

            #  Datos Receptor
            direction_values_receptor = {
                'Calle': receptor_street, 'Código Postal': receptor_zip,
                'Ciudad': receptor_city, 'Departamento': receptor_state,
                'País': receptor_country
            }
            vdr = self.examine_values(direction_values_receptor, 'cliente')
            receptor_fel.set_direccion(vdr['Calle'], vdr['Código Postal'], vdr['Ciudad'], vdr['Departamento'],
                                       vdr['País'])
            """Actualización 22/04/2021
                            Mejora para envío de datos si el cliente es un consumidor final."""
            if instance_partner.its_final_consumer:
                receptor_name = 'Consumidor Final'
            """--------Fin Actualización 22/04/2021-----------"""
            data_values_receptor = {
                'Correo': receptor_email, 'Nit': instance_partner.vat,
                'Razón Social': receptor_name
            }
            dvr = self.examine_values(data_values_receptor, 'cliente')
            receptor_fel.set_datos_receptor(dvr['Correo'], dvr['Nit'], dvr['Razón Social'])

            certify_fel_dte.set_datos_receptor(receptor_fel)

            gt = timezone('America/Guatemala')
            utc_dt = datetime.now(tz=UTC).astimezone(gt)
            custom_dt = datetime.combine(move.invoice_date, datetime.min.time()) \
                if move.invoice_date and move.invoice_date < fields.Date.today() else False
            dt = utc_dt if not custom_dt else custom_dt

            dtime_emission = False
            if instance_company.fel_provider in ['IN', 'MP']:
                dtime_emission = dt.strftime("%Y-%m-%dT%H:%M:%S") + '-06:00'
            elif instance_company.fel_provider in ['DI', 'CO']:
                dtime_emission = dt.strftime("%Y-%m-%dT%H:%M:%S")
            elif instance_company.fel_provider == 'ECO':
                dtime_emission = dt.strftime("%Y-%m-%d")

            if move.journal_id:
                """Actualización del 10/05/2021
                    Mejora para obtención de tipo de documento para emisión."""
                if move.invoice_doc_type == move._get_sequence().l10n_latam_document_type_id:
                    dte_type = move._get_sequence().l10n_latam_document_type_id.doc_code_prefix
                else:
                    raise ValidationError(
                        'La secuencia del diario seleccionado no concuerda con el tipo de documento a emitir.'
                    )
            else:
                raise ValidationError('No tienes un diario seleccionado.')
            certify_fel_dte.set_datos_generales(move.currency_id.name, dtime_emission, dte_type.strip())
            """---------Fin actualización 10/05/2021-----------"""

            # # identificador unico del dte del cliente
            """Actualización del 28.10.2021 para eliminar funcionamiento de campos dobres paras datos FEL"""
            identifier = move.name
            if not move.key_identifier:
                identifier = self.set_key_identifier()
                move.key_identifier = identifier
            elif move.key_identifier:
                identifier = move.key_identifier
            certify_fel_dte.set_clave_unica(identifier)
            """Actualización del 28.10.2021 para eliminar funcionamiento de campos dobres paras datos FEL"""

            if move.state == 'contingency' and instance_company.fel_provider != 'ECO':  # USO PARA CONTINGENCIAS
                if dte_type.strip() == 'NCRE':
                    access_number = move.fel_num_acceso_ncre
                elif dte_type.strip() == 'NDEB':
                    access_number = move.fel_num_acceso_ndeb
                else:
                    access_number = move.fel_num_acceso
                certify_fel_dte.set_acceso(access_number)

            export = ''
            """Cambios 16.06.2021 para Exentos"""
            exempt = False
            """Actualización 16.06.2021
                mejora para reducir código y seguir el principio Dont repeat your self en frases FEL.
            """

            def set_phrases(phrase, type_phrase):
                if str(phrase) == '1' and str(type_phrase) == '4':
                    # agregar las frases exportacion
                    certify_fel_dte.frase_fel.set_frase(str(phrase), str(type_phrase))
                    export = "SI"
                    certify_fel_dte.set_exportacion(export)
                    return False, export
                elif str(x.phrase) in ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12') and str(
                        x.type) == '4':
                    certify_fel_dte.frase_fel.set_frase(str(phrase), str(type_phrase))
                    return True, ''
                elif str(x.phrase) and str(x.type):
                    certify_fel_dte.frase_fel.set_frase(str(phrase), str(type_phrase))
                    return False, ''

            """------------Fin Actualización 16.06.2021-----------"""

            # agregar las frases
            phrases = dict()
            if dte_type.strip() in ['FACT', 'FCAM']:
                # indicador de las frases exportacion
                if instance_partner.property_account_position_id:
                    for x in instance_partner.property_account_position_id.fel_phrases_ids:
                        """Actualización 16.06.2021
                            mejora para reducir código y seguir el principio Dont repeat your self en frases FEL.
                        """
                        if x.phrase not in phrases.keys() or phrases.get(x.phrase, False) != x.type:
                            phrases.update({x.phrase: x.type})
                            exempt, export = set_phrases(x.phrase, x.type)
                        """------------Fin Actualización 16.06.2021-----------"""
                elif instance_partner.fel_phrases_ids:
                    for t in instance_partner.fel_phrases_ids:
                        """Actualización 16.06.2021
                            mejora para reducir código y seguir el principio Dont repeat your self en frases FEL.
                        """
                        if t.phrase not in phrases.keys() or phrases.get(t.phrase, False) != t.type:
                            phrases.update({t.phrase: t.type})
                            exempt, export = set_phrases(t.phrase, t.type)
                        """------------Fin Actualización 16.06.2021-----------"""
                """Cambios 17/03/2021 para Exentos"""
                if instance_company.fel_phrases_ids:
                    for p in instance_company.fel_phrases_ids:
                        if p.phrase not in phrases.keys() or phrases.get(p.phrase, False) != p.type:
                            phrases.update({p.phrase: p.type})
                            certify_fel_dte.frase_fel.set_frase(str(p.phrase), str(p.type))

            """Mejora para envio de más de un tipo de impuesto"""
            tax_total = 0
            """Mejora para envio de más de un tipo de impuesto"""
            t = None
            taxes = []
            for idx, line in enumerate(move.invoice_line_ids):
                item = provider.item()

                item.set_numero_linea(idx + 1)
                if line.product_id.type == 'service':
                    goods_service = 'S'
                    item.set_bien_o_servicio(goods_service)
                elif line.product_id.type == 'consu' or line.product_id.type == 'product':
                    goods_service = 'B'
                    item.set_bien_o_servicio(goods_service)
                item.set_cantidad(line.quantity)
                item.set_unidad_medida(line.product_id.uom_id.name)
                description_sanitized = self.examine_values(
                    {'description': line.display_name or line.name}, 'líneas de factura')
                description = description_sanitized.get('description')
                item.set_descripcion(description)
                item.set_precio_unitario(self.truncate(line.price_unit, 10))
                # Descuentos
                desc = (line.price_unit * line.quantity * line.discount) / 100
                price = line.line_total + desc
                item.set_precio(self.truncate(price, 10))  # a este no aplicar el descuento
                # Descuentos
                item.set_descuento(self.truncate(desc, 10))
                """Mejora para envio de tipo de impuesto TIMBRE DE PRENSA"""
                """RECORDATORIO, CAMBIOS EN TD GENERICO METODO set_total_amount ARCHIVO account_move.py"""
                amount_tax = line.tax_ids.filtered(lambda tax: tax.tax_group_id.name == 'TIMBRE DE PRENSA').amount
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxable_amount = price * line.quantity / 1.12
                sum_tax = (amount_tax * taxable_amount) / 100
                item.set_total(self.truncate(line.line_total + sum_tax or 0.0, 10))
                """Mejora para envio de tipo de impuesto TIMBRE DE PRENSA"""

                # no aplica para Notas de Abono ni para Recibos, ni recibo por donación
                if dte_type.strip() not in ['NABN', 'RECI', 'RDON']:
                    for tax in line.tax_ids:
                        tax_item = provider.impuesto()

                        if tax.tax_group_id:
                            tax_short_name = tax.tax_group_id.name
                            if tax_short_name == 'IVA':
                                if instance_company.fel_iva == 'GEN':
                                    if export == 'SI':
                                        t = move.tax(2, self.truncate(line.line_total, 10), 0)
                                    else:
                                        """Cambios 17/03/2021 para Exentos"""
                                        if exempt:
                                            t = move.tax(2, self.truncate(line.line_total, 10), 0)
                                        else:
                                            taxable_amount = self.truncate(
                                                abs(line.price_unit * line.quantity - desc) / (1 + (tax.amount / 100)),
                                                10)
                                            t = move.tax(1, taxable_amount,
                                                         self.truncate((tax.amount * taxable_amount) / 100, 10))
                                            """Cambios 17/03/2021 para Exentos"""
                                elif instance_company.fel_iva == 'PEQ' or instance_company.fel_iva == 'EXE':
                                    t = move.tax(2, self.truncate(line.line_total, 10), 0)
                                """Mejora para envío de más de un tipo de impuesto"""
                            elif tax_short_name == 'RETENCIONES':
                                continue
                            elif tax_short_name == 'IDP':
                                continue
                            elif tax_short_name == 'TIMBRE DE PRENSA':
                                if instance_company.fel_iva == 'GEN':
                                    taxable_amount = abs(line.price_unit * line.quantity - desc) / 1.12
                                    t = move.tax(1, self.truncate(taxable_amount, 10),
                                                 self.truncate((tax.amount * taxable_amount) / 100, 10))
                                elif instance_company.fel_iva == 'PEQ' or instance_company.fel_iva == 'EXE':
                                    t = move.tax(2, self.truncate(line.line_total, 10), 0)
                                """Mejora para envío de más de un tipo de impuesto"""
                            else:
                                raise ValidationError('El impuesto en la(s) línea(s) tiene grupo'
                                                      ' de impuestos no permitido.')
                            tax_total += t['tax_amount']
                            tax_item.set_monto_gravable(t['taxable_amount'])
                            tax_item.set_monto_impuesto(t['tax_amount'])
                            tax_item.set_codigo_unidad_gravable(t['taxable_unit_code'])
                            tax_item.set_nombre_corto(tax_short_name)
                            item.set_impuesto(tax_item)

                            """Mejora para envio de más de un tipo de impuesto"""
                            if tax_short_name not in [t['tax'] for t in taxes]:
                                taxes.append({'tax': tax_short_name, 'total_tax': t['tax_amount']})
                            else:
                                for tax in taxes:
                                    if tax_short_name == tax['tax']:
                                        tax['total_tax'] += t['tax_amount']
                            """Mejora para envio de más de un tipo de impuesto"""
                        else:
                            raise ValidationError('El impuesto en la(s) línea(s) no tiene grupo de impuestos.')
                # no aplica para Notas de Abono ni para Recibos, ni recibo por donación
                certify_fel_dte.agregar_item(item)

            if instance_company.fel_provider != "ECO":
                # Totales
                total_fel = provider.totales()
                total_fel.set_gran_total(self.truncate(move.amount, 10))
                # no aplica para Notas de Abono ni para Recibos, ni recibo por donación
                if dte_type.strip() not in ['NABN', 'RECI', 'RDON']:
                    """Mejora para envío de más de un tipo de impuesto"""
                    for tax in taxes:
                        taxes_total = provider.total_impuesto()
                        taxes_total.set_nombre_corto(tax['tax'])
                        taxes_total.set_total_monto_impuesto(self.truncate(tax['total_tax'], 10))
                        total_fel.set_total_impuestos(taxes_total)
                        """Mejora para envio de más de un tipo de impuesto"""
                    # no aplica para Notas de Abono ni para Recibos, ni recibo por donación
                certify_fel_dte.agregar_totales(total_fel)

            if instance_company.fel_provider == 'IN':
                if instance_company.adendas_ids:
                    for adenda in instance_company.adendas_ids:
                        """Mejora realizada el 20/03/2021. 
                            Para permitir que las adendas sean enviadas segun tipo de documento o sin tipo definido.
                            Si no se ha definido tipo, las adendas serán para cualquier tipo de doc,
                            si se ha definido tipo de documento, se evaluara que sea el mismo tipo de la emision.
                            caso contrario, no se enviaran las adendas."""
                        if not adenda.doc_type_id:
                            access = True
                        elif adenda.doc_type_id.doc_code_prefix.strip() == dte_type.strip():
                            access = True
                        else:
                            access = False
                        if access:
                            """-------Fin de mejora 20/03/2021--------"""
                            # # agregar adendas al gusto
                            fel_adenda = InfileFel.adenda()

                            fel_adenda.nombre = adenda.name
                            if adenda.model_id != 'account.move':
                                if adenda.model_id == 'res.partner':
                                    fel_adenda.valor = str(move.partner_id[adenda.field_id.name])
                                elif adenda.model_id == 'res.users':
                                    fel_adenda.valor = str(move.user_id[adenda.field_id.name])
                                elif adenda.model_id == 'res.company':
                                    fel_adenda.valor = str(move.company_id[adenda.field_id.name])
                                elif adenda.model_id == 'account.payment.term':
                                    fel_adenda.valor = str(move.invoice_payment_term_id[adenda.field_id.name])
                                elif adenda.model_id == 'sale.order':
                                    for line in move.invoice_line_ids:
                                        order = line.sale_line_ids.mapped('order_id')
                                        if order:
                                            if adenda.field_id.name == 'partner_id':
                                                value = str(order.partner_id.name) \
                                                    if order.partner_id.company_type == 'person' else ''
                                                fel_adenda.valor = value
                                            else:
                                                fel_adenda.valor = str(order[adenda.field_id.name])
                                        else:
                                            """Actualización del 07.05.2021 
                                                Quitar el warning fue necesario debido a que 
                                                no alertaba de nada, nunca aparecia esto, 
                                                y no permitia la emision del documento con FEL, solo en odoo.
                                                A cambio coloqué fel_adenda.valor = ''"""
                                            fel_adenda.valor = ''
                                elif adenda.model_id == 'product.template':
                                    product_adendas = ''
                                    for idx, line in enumerate(move.invoice_line_ids):
                                        product_adendas += str(idx + 1) + " @ " \
                                                           + str(line.product_id[adenda.field_id.name]) + " | "
                                    fel_adenda.valor = product_adendas
                            else:
                                if adenda.field_id.ttype == 'many2one':
                                    fel_adenda.valor = str(move[adenda.field_id.name].name)
                                elif adenda.field_id.name == 'display_name':
                                    sequence = move._get_sequence()
                                    number = '%%0%sd' % sequence.padding % \
                                             sequence._get_current_sequence().number_next_actual
                                    name = '%s%s' % (sequence.prefix or '', number)
                                    fel_adenda.valor = name
                                else:
                                    fel_adenda.valor = str(move[adenda.field_id.name])
                            certify_fel_dte.agregar_adenda(fel_adenda)
            elif instance_company.fel_provider == 'DI':
                # # agregar adendas al gusto
                fel_adenda = DigifactFel.adenda()
                fel_adenda.internal_reference = identifier
                fel_adenda.reference_date = dtime_emission
                fel_adenda.validate_internal_reference = move.validate_internal_reference
                certify_fel_dte.agregar_adenda(fel_adenda)
            elif instance_company.fel_provider == 'ECO':
                # # agregar adendas al gusto
                for idx, adenda in enumerate(instance_company.adendas_ids):
                    if not adenda.doc_type_id:
                        access = True
                    elif adenda.doc_type_id.doc_code_prefix.strip() == dte_type.strip():
                        access = True
                    else:
                        access = False
                    if access:
                        fel_adenda = EcofacturaFel.adenda()
                        concatenate_name_value = '0' if 0 < idx + 1 < 10 else ''
                        fel_adenda.name = 'TrnCampAd' + concatenate_name_value + str(idx + 1)
                        if adenda.model_id != 'account.move':
                            if adenda.model_id == 'res.partner':
                                fel_adenda.value = str(move.partner_id[adenda.field_id.name])
                            elif adenda.model_id == 'res.users':
                                fel_adenda.value = str(move.user_id[adenda.field_id.name])
                            elif adenda.model_id == 'res.company':
                                fel_adenda.value = str(move.company_id[adenda.field_id.name])
                            elif adenda.model_id == 'account.payment.term':
                                fel_adenda.value = str(move.invoice_payment_term_id[adenda.field_id.name])
                            elif adenda.model_id == 'sale.order':
                                for line in move.invoice_line_ids:
                                    order = line.sale_line_ids.mapped('order_id')
                                    if order:
                                        if adenda.field_id.name == 'partner_id':
                                            value = str(order.partner_id.name) \
                                                if order.partner_id.company_type == 'person' else ''
                                            fel_adenda.value = value
                                        else:
                                            fel_adenda.value = str(order[adenda.field_id.name])
                                    else:
                                        fel_adenda.value = ''
                            elif adenda.model_id == 'product.template':
                                product_adendas = ''
                                for idx, line in enumerate(move.invoice_line_ids):
                                    product_adendas += str(idx + 1) + " @ " \
                                                       + str(line.product_id[adenda.field_id.name]) + " | "
                                fel_adenda.value = product_adendas
                        else:
                            if adenda.field_id.ttype == 'many2one':
                                fel_adenda.value = str(move[adenda.field_id.name].name)
                            elif adenda.field_id.name == 'display_name':
                                sequence = move._get_sequence()
                                number = '%%0%sd' % sequence.padding % \
                                         sequence._get_current_sequence().number_next_actual
                                name = '%s%s' % (sequence.prefix or '', number)
                                fel_adenda.value = name
                            else:
                                fel_adenda.valor = str(move[adenda.field_id.name])
                        certify_fel_dte.agregar_adenda(fel_adenda)

            if dte_type == 'NCRE':
                """Actualizacion del 25.10.2021 
                      Para cambiar el envío de posibles caracteres especiales en el campo motivo de ajuste
                       Mejora: ascii(move.reason_note) if isinstance(move.reason_note, str) else ascii('Anulación')
                """
                credit_notes_complement = provider.complemento_notas()
                data_notes = move.data_notes(dte_type.strip())
                reason_sanitized = self.examine_values({'reason': move.reason_note
                if isinstance(move.reason_note, str) else 'Anulación'}, 'Nota de crédito')
                reason = reason_sanitized.get('reason')
                credit_notes_complement.agregar("ANTIGUO" if move.ancient_regime else "",
                                                reason, data_notes['fel_date'],
                                                data_notes['series'], data_notes['uuid'], data_notes['doc_dte'])
                certify_fel_dte.agregar_complemento(credit_notes_complement)
            elif dte_type.strip() == 'FCAM':
                exchange_complement = provider.complemento_cambiaria()
                expiration_date = move.invoice_date_due
                exchange_complement.agregar(1, expiration_date, self.truncate(move.amount, 10))
                certify_fel_dte.agregar_complemento(exchange_complement)
            elif dte_type == 'FESP':
                especial_type = "2" if instance_company.fel_provider == 'ECO' else "CUI"
                certify_fel_dte.set_tipo_especial(especial_type)  # instance_partner.l10n_latam_identification_type_id.name
                if instance_company.fel_provider != 'ECO':
                    fesp_complement = provider.complemento_especial()
                    """Actualizacion del 04/05/2021 
                        Para cambiar porcentaje para calculo de ISR retenido, 
                        del 7 al 5%. Segun nueva instruccion SAT
                        Nueva reforma hecha por SAT."""
                    isr_retencion = self.truncate(t['taxable_amount'] * (5 / 100), 10)
                    """----------FIN-----------"""
                    free_total = self.truncate(abs(t['taxable_amount'] - isr_retencion), 10)
                    fesp_complement.agregar(isr_retencion, tax_total, free_total)
                    certify_fel_dte.agregar_complemento(fesp_complement)
            elif dte_type.strip() == 'NDEB':
                debit_notes_complement = provider.complemento_notas()
                data_notes = move.data_notes(dte_type.strip())
                reason_sanitized = self.examine_values(
                    {'reason': move.reason_note
                    if isinstance(move.reason_note, str) else 'Anulación'}, 'Nota de débito')
                reason = reason_sanitized.get('reason')
                debit_notes_complement.agregar("ANTIGUO" if move.ancient_regime else "",
                                               reason, data_notes['fel_date'],
                                               data_notes['series'], data_notes['uuid'], data_notes['doc_dte'])
                certify_fel_dte.agregar_complemento(debit_notes_complement)
            if export == 'SI':
                if instance_company.fel_provider == 'ECO':
                    receptor_fel.set_purchaser_code(instance_partner.ref if instance_partner.ref else False)
                export_complement = provider.complemento_exportacion()
                if not move.invoice_incoterm_id:
                    raise ValidationError('No puedes realizar una factura de exportación '
                                          'sin INCONTERM, llénalo en la factura.')
                if instance_company.fel_provider == 'IN':
                    if not instance_company.exporter_code:
                        raise ValidationError('No puedes realizar una factura de exportación con INFILE'
                                              'sin Código de exportación del emisor.')
                elif instance_company.fel_provider in ['DI', 'MP']:
                    if not move.partner_shipping_id:
                        raise ValidationError('No puedes realizar una factura de exportación con DIGIFACT'
                                              'sin los datos del consignatario de destino.')
                    if move.partner_shipping_id:
                        if not move.partner_shipping_id.name:
                            raise ValidationError('No puedes realizar una factura de exportación con DIGIFACT'
                                                  'sin el nombre del consignatario de destino.')
                        if not move.partner_shipping_id.street:
                            raise ValidationError('No puedes realizar una factura de exportación con DIGIFACT'
                                                  'sin enviar la dirección del consignatario de destino.')

                export_complement.agregar(move.partner_shipping_id.name
                                          if move.partner_shipping_id and move.partner_shipping_id.name else '',
                                          move.partner_shipping_id.street
                                          if move.partner_shipping_id and move.partner_shipping_id.street else '',
                                          move.partner_shipping_id.ref
                                          if move.partner_shipping_id and move.partner_shipping_id.ref else ' ',
                                          instance_partner.name, instance_partner.street, instance_partner.ref
                                          if instance_partner.ref else ' ',
                                          move.invoice_origin, move.invoice_incoterm_id.code,
                                          instance_company.legal_name, instance_company.exporter_code)
                certify_fel_dte.agregar_complemento(export_complement)

            certify_fel = False
            if instance_company.fel_provider in ['IN', 'ECO']:
                credentials = [instance_company.fel_pass, instance_company.fel_pass_sign,
                               instance_company.fel_user, instance_company.vat, instance_company.email]
                for credential in credentials:
                    if not credential:
                        raise ValidationError('La compañía no está bien configurada para el proveedor INFILE. '
                                              'Hay campos sin datos.')

                certify_fel = certify_fel_dte.certificar(instance_company.fel_pass, instance_company.fel_pass_sign,
                                                         instance_company.fel_user,
                                                         instance_company.vat.replace("-", ""),
                                                         instance_company.email, instance_company)
            elif instance_company.fel_provider == 'DI':
                credentials = [instance_company.token, instance_company.vat_digifact]
                for credential in credentials:
                    if not credential:
                        raise ValidationError('La compañía no está bien configurada para el proveedor DIGIFACT. '
                                              'Hay campos sin datos. Por favor revise.')
                certify_fel = certify_fel_dte.certificar(instance_company.token,
                                                         instance_company.vat_digifact, instance_company)

            elif instance_company.fel_provider in ['CO', 'MP']:
                if not instance_company.token:
                    raise ValidationError('La compañía no está bien configurada para el proveedor CONTAP o MEGAPRINT'
                                          'Falta el Token de autenticación. Por favor revise.')
                certify_fel = certify_fel_dte.certificar(instance_company.token, instance_company)

            _logger.info("HAZ PROBADO CERTIFICAR FEL!")
            """Actualización del 28.10.2021 para eliminar funcionamiento de campos dobres paras datos FEL"""

            certificate = move.response_dte_fel(certify_fel, 'doc_xml_generated', 'certify_xml',
                                                'signed_xml', 'fel_uuid', 'fel_date',
                                                'fel_serie', 'fel_number', move.id)
            """Actualización del 28.10.2021 para eliminar funcionamiento de campos dobres paras datos FEL"""
            return certificate

    def button_cancel(self):
        default_move_type = self._context.get('default_move_type', False)
        default_dte_type = self._context.get('default_invoice_doc_type', False)
        for move in self:
            if move.company_id.its_fel and default_move_type in ['out_invoice', 'out_refund'] \
                    or default_move_type == 'in_invoice' and default_dte_type == 5:

                if move.company_id.fel_provider == 'IN':
                    dte_fel_to_cancel = InfileFel.fel_dte()
                elif move.company_id.fel_provider == 'DI':
                    dte_fel_to_cancel = DigifactFel.fel_dte()
                elif move.company_id.fel_provider == 'MP':
                    dte_fel_to_cancel = MegaPrintFel.fel_dte()
                elif move.company_id.fel_provider == 'ECO':
                    dte_fel_to_cancel = EcofacturaFel.fel_dte()
                else:
                    raise ValidationError('No has seleccionado a ningún proveedor para la emisión FEL. '
                                          'Debe ser configurado en la compañía emisora. '
                                          'Por favor hazlo o comunícate con administración.')

                gt = timezone('America/Guatemala')
                utc_dt = datetime.now(tz=UTC).astimezone(gt)
                date_cancel = utc_dt.strftime("%Y-%m-%dT%H:%M:%S") + '-06:00'
                if not move.partner_id.vat:
                    raise ValidationError('El cliente no tiene NIT. Falta agregarlo.')

                fel_date = move.fel_date
                fel_uuid = move.fel_uuid

                if not fel_date or not fel_uuid:
                    raise ValidationError('No existe documento FEL para anular.')

                if move.company_id.fel_provider in ['IN', 'ECO']:
                    credentials = [move.company_id.fel_pass, move.company_id.fel_pass_sign,
                                   move.company_id.fel_user, move.company_id.vat, move.company_id.email]
                elif move.company_id.fel_provider in ['DI', 'MP']:
                    credentials = [move.company_id.token]
                else:
                    raise ValidationError('No ha seleccionado a ningún proveedor para la emisión FEL. '
                                          'Debe ser configurado en la compañía emisora. '
                                          'Por favor hágalo o comuníquese con administración.')

                for credential in credentials:
                    if not credential:
                        raise ValidationError('La compañía no está bien configurada. Hay campos sin datos.')

                # # identificador unico del dte del cliente
                identifier = move.name
                if not move.key_identifier:
                    identifier = self.set_key_identifier()
                    move.key_identifier = identifier
                elif move.key_identifier:
                    identifier = move.key_identifier
                dte_fel_to_cancel.set_clave_unica(identifier)

                cancel_fel = False
                if move.company_id.fel_provider == 'IN':
                    cancel_fel = dte_fel_to_cancel.anular(date_cancel,
                                                          move.company_id.vat.replace("-", ""),
                                                          fel_date,
                                                          move.partner_id.vat.replace("-", ""), fel_uuid,
                                                          '**Cancelación**', move.company_id.fel_pass,
                                                          move.company_id.fel_pass_sign, move.company_id.fel_user,
                                                          move.company_id.vat, move.company_id.email,
                                                          move.company_id
                                                          )
                elif move.company_id.fel_provider == 'DI':
                    cancel_fel = dte_fel_to_cancel.anular(date_cancel,
                                                          move.company_id.vat.replace("-", ""),
                                                          fel_date,
                                                          move.partner_id.vat.replace("-", ""), fel_uuid,
                                                          '**Cancelación**', move.company_id.token,
                                                          move.company_id.vat_digifact,
                                                          move.company_id
                                                          )
                elif move.company_id.fel_provider == 'MP':
                    cancel_fel = dte_fel_to_cancel.anular(date_cancel,
                                                          move.company_id.vat.replace("-", ""),
                                                          fel_date,
                                                          move.partner_id.vat.replace("-", ""), fel_uuid,
                                                          '**Cancelación**', move.company_id.token,
                                                          move.company_id
                                                          )
                elif move.company_id.fel_provider == 'ECO':
                    cancel_fel = dte_fel_to_cancel.anular(fel_uuid, '**Anulación**',
                                                          move.company_id.fel_pass, move.company_id.fel_pass_sign,
                                                          move.company_id.fel_user,
                                                          move.company_id.vat.replace("-", ""), move.company_id)

                """Actualización del 28.10.2021 para eliminar funcionamiento de campos dobres paras datos FEL"""
                canceled = move.response_dte_fel(cancel_fel, 'doc_xml_cancel_generated', 'certify_cancel_xml',
                                                 'signed_cancel_xml', 'fel_uuid_cancel', 'fel_date_cancel',
                                                 'fel_series_cancel', 'fel_number_cancel', move.id)
                """Actualización del 28.10.2021 para eliminar funcionamiento de campos dobres paras datos FEL"""

                if canceled:
                    res = super(AccountMoveInherited, self).button_cancel()
                    return res
            else:
                res = super(AccountMoveInherited, self).button_cancel()
                return res

    def action_post(self):
        default_move_type = self._context.get('default_move_type', False)
        default_dte_type = self._context.get('default_invoice_doc_type', False)
        if self.company_id.its_fel and default_move_type in ['out_invoice', 'out_refund']:
            certificate_dte_fel = self.dte_fel()
            if certificate_dte_fel:
                """Actualización del 16.06.2021,
                    Obtiene el formato .pdf de la actual emisión de Megaprint
                """
                if self.company_id.fel_provider == "MP":
                    """Actualizaciones del 09.09.2021
                        Mejoras para manejar errores luego de certificaciones FEL
                    """
                    try:
                        self.get_pdf()
                    except Exception as e:
                        """Actualización del 28.10.2021 para eliminar funcionamiento de campos dobres paras datos FEL"""
                        # dte_type = self._get_sequence().l10n_latam_document_type_id.doc_code_prefix
                        """Actualización del 28.10.2021 para eliminar funcionamiento de campos dobres paras datos FEL"""
                        error_msg = {'resultado': False,
                                     "descripcion_errores": [{
                                         "mensaje_error": tools.ustr(e), "fuente": '',
                                         "categoria": '', "numeral": '#', "validacion": ''
                                     }], 'archivo': 'Hubo un error en la comunicación.',
                                     'descripcion': tools.ustr(e)
                                     }
                        """Actualización del 28.10.2021 para eliminar funcionamiento de campos dobres paras datos FEL"""

                        """Actualización del 28.10.2021 para eliminar funcionamiento de campos dobres paras datos FEL"""
                        error_msg.update({"xml_plano": self.doc_xml_generated})
                        self.response_dte_fel(error_msg, 'doc_xml_generated', 'certify_xml',
                                              'signed_xml', 'fel_uuid', 'fel_date',
                                              'fel_serie', 'fel_number', self.id)
                        """--------Fin Actualización del 09.09.2021---------"""
                """-----Fin Actualización del 16.06.2021------"""

                """Actualizaciones del 09.09.2021
                    Mejoras para manejar errores luego de certificaciones FEL
                """
                try:
                    res = super(AccountMoveInherited, self).action_post()
                    return res
                except Exception:
                    pass
                """--------Fin Actualización del 09.09.2021---------"""
        elif self.company_id.its_fel and default_move_type == 'in_invoice' and default_dte_type == 5:
            certificate_dte_fel = self.dte_fel()
            if certificate_dte_fel:
                res = super(AccountMoveInherited, self).action_post()
                return res
        else:
            res = super(AccountMoveInherited, self).action_post()
            return res

    def action_server_massive_post_fel(self):
        """Actualización del 7/05/2021
            Acción de servidor para la emisión masiva de DTEs.
        """
        for record in self.filtered(
                lambda move: move.move_type in ['out_invoice', 'out_refund'] and move.state == 'draft'):
            record.with_context(default_move_type=record.move_type).action_post()

    def _get_sequence(self):
        """Actualización del 10/05/2021
            Sobreescritura de método _get_sequence para obtener
            la secuencia usada según el tipo de documento del doc a emitir con FEL.
        """
        self.ensure_one()
        journal = self.journal_id
        if self.move_type in ('entry', 'out_invoice', 'in_invoice', 'out_receipt', 'in_receipt') \
                or not journal.refund_sequence:
            return journal.sequence_id
        elif self.move_type == 'out_refund' and journal.refund_sequence:
            doc_type = self.invoice_doc_type.doc_code_prefix or ''
            if doc_type.strip() == 'NCRE':
                return journal.refund_sequence_id
            elif doc_type.strip() == 'NDEB':
                return journal.ndeb_sequence_id
            elif doc_type.strip() == 'NABN':
                return journal.nabn_sequence_id
        else:
            return journal.refund_sequence_id

    @api.constrains('invoice_doc_type')
    def check_invoice_doc_type(self):
        """Metodo para chequear el tipo de documento ingresado en las facturas de clientes."""
        document_type_ids = (self.env.ref('l10n_gt_td_generic.dc_fact').id, self.env.ref('l10n_gt_td_generic.dc_reci').id,
                             self.env.ref('l10n_gt_td_generic.dc_fcam').id)
        if self.move_type == 'out_invoice' and self.invoice_doc_type.id not in document_type_ids:
            raise ValidationError('Debe ingresar únicamente el tipo de documento: Factura, Factura Cambiaria o Recibo')

    def get_pdf(self):
        """Función útil únicamente para Megaprint.
            Obtiene el formato .pdf del UUID de la emisión indicada.
        """
        """Actualización del 28.10.2021 para eliminar funcionamiento de campos dobres paras datos FEL"""
        uuid = self.fel_uuid
        url = "https://apiv2.ifacere-fel.com/api/retornarPDF"
        xml = """<?xml version="1.0" encoding="UTF-8"?> 
                <RetornaPDFRequest> 
                <uuid>""" + uuid + """</uuid> 
                </RetornaPDFRequest>"""
        token = self.company_id.token
        headers = {
            'Authorization': "bearer " + token,
            'Content-Type': 'application/xml; charset=utf-8'
        }
        r = requests.post(url=url, data=xml.encode('utf-8'), headers=headers)
        pdf = False
        for item in r.text.split("</pdf>"):
            if "<pdf>" in item:
                pdf = item[item.find("<pdf>") + len("<pdf>"):]
        if pdf:
            self.env['ir.attachment'].create({
                'name': "PDF",
                'type': 'binary',
                'datas': pdf,
                'store_fname': "PDF",
                'res_model': self._name,
                'res_id': self.id,
                'mimetype': 'application/x-pdf'
            })
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': 'No ha sido posible obtener el documento .pdf que Megaprint genera.',
                    'sticky': True,
                    'type': 'danger'
                }
            }
