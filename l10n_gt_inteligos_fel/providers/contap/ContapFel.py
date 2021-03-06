from random import randint
import base64
from . import ContapEmisor
import json
from . import ContapReceptor
import requests  # pip3 install requests
import logging

_logger = logging.getLogger(__name__)


class complemento_notas():
    def __init__(self):
        self.xml = ''
        self.lista_complementos = []

    def agregar(self, RegimenAntiguo, MotivoAjuste, FechaEmisionDocumentoOrigen, SerieDocumentoOrigen,
                NumeroAutorizacionDocumentoOrigen, NumeroDocumentoOrigen):
        self.lista_complementos.append({"RegimenAntiguo": RegimenAntiguo,
                                        "MotivoAjuste": MotivoAjuste,
                                        "FechaEmisionDocumentoOrigen": FechaEmisionDocumentoOrigen,
                                        "NumeroDocumentoOrigen": NumeroDocumentoOrigen,
                                        "SerieDocumentoOrigen": SerieDocumentoOrigen,
                                        "NumeroAutorizacionDocumentoOrigen": NumeroAutorizacionDocumentoOrigen
                                        })

    def to_xml(self):
        self.xml = ''
        if (len(self.lista_complementos) > 0):
            self.xml += '<dte:Complemento IDComplemento="text" NombreComplemento="GT_Complemento_Referencia_Nota-0.1.0" URIComplemento="GT_Complemento_Referencia_Nota-0.1.0.xsd">'

            for complemento in self.lista_complementos:
                if (complemento["RegimenAntiguo"] == 'ANTIGUO'):
                    self.xml += '<cno:ReferenciasNota xmlns:cno="http://www.sat.gob.gt/face2/ComplementoReferenciaNota/0.1.0" RegimenAntiguo="Antiguo" FechaEmisionDocumentoOrigen="' + str(
                        complemento["FechaEmisionDocumentoOrigen"]) + '" MotivoAjuste="' + str(
                        complemento["MotivoAjuste"]) + '" NumeroAutorizacionDocumentoOrigen="' + str(
                        complemento["NumeroAutorizacionDocumentoOrigen"]) + '" NumeroDocumentoOrigen="' + str(
                        complemento["NumeroDocumentoOrigen"]) + '" SerieDocumentoOrigen="' + str(
                        complemento["SerieDocumentoOrigen"]) + '" Version="0.0" />'
                # self.xml += '<cno:ReferenciasNota xmlns:cno="http://www.sat.gob.gt/face2/ComplementoReferenciaNota/0.1.0"  NumeroDocumentoOrigen="text" Version="0.0" RegimenAntiguo="Antiguo" MotivoAjuste="'+ str(complemento["MotivoAjuste"])  +'" FechaEmisionDocumentoOrigen="'+ str(complemento["FechaEmisionDocumentoOrigen"])  +'" SerieDocumentoOrigen="'+ str(complemento["SerieDocumentoOrigen"])  +'" NumeroAutorizacionDocumentoOrigen="'+ str(complemento["NumeroAutorizacionDocumentoOrigen"]) +'/>'
                else:
                    self.xml += '<cno:ReferenciasNota xmlns:cno="http://www.sat.gob.gt/face2/ComplementoReferenciaNota/0.1.0" FechaEmisionDocumentoOrigen="' + str(
                        complemento["FechaEmisionDocumentoOrigen"]) + '" MotivoAjuste="' + str(
                        complemento["MotivoAjuste"]) + '" NumeroAutorizacionDocumentoOrigen="' + str(
                        complemento["NumeroAutorizacionDocumentoOrigen"]) + '" Version="0.0" />'

            self.xml += '</dte:Complemento>'
        return self.xml


class complemento_exportacion():
    def __init__(self):
        self.xml = ''
        self.lista_complementos = []

    def agregar(self, NombreConsignatarioODestinatario, DireccionConsignatarioODestinatario,
                CodigoConsignatarioODestinatario, NombreComprador, DireccionComprador, CodigoComprador, OtraReferencia,
                INCOTERM, NombreExportador, CodigoExportador):
        self.lista_complementos.append({"NombreConsignatarioODestinatario": NombreConsignatarioODestinatario,
                                        "DireccionConsignatarioODestinatario": DireccionConsignatarioODestinatario,
                                        "CodigoConsignatarioODestinatario": CodigoConsignatarioODestinatario,
                                        "NombreComprador": NombreComprador,
                                        "DireccionComprador": DireccionComprador,
                                        "CodigoComprador": CodigoComprador,
                                        "OtraReferencia": OtraReferencia,
                                        "INCOTERM": INCOTERM,
                                        "NombreExportador": NombreExportador,
                                        "CodigoExportador": CodigoExportador
                                        })

    def to_xml(self):
        self.xml = ''
        if (len(self.lista_complementos) > 0):
            self.xml += '<dte:Complemento IDComplemento="text" NombreComplemento="GT_Complemento_Exportaciones" URIComplemento="http://www.sat.gob.gt/face2/ComplementoExportaciones/0.1.0">'

            for complemento in self.lista_complementos:
                self.xml += '<cex:Exportacion Version="1" xsi:schemaLocation="http://www.sat.gob.gt/face2/ComplementoExportaciones/0.1.0" xmlns:cex="http://www.sat.gob.gt/face2/ComplementoExportaciones/0.1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                self.xml += '<cex:NombreConsignatarioODestinatario>' + str(
                    complemento["NombreConsignatarioODestinatario"]) + '</cex:NombreConsignatarioODestinatario>'
                self.xml += '<cex:DireccionConsignatarioODestinatario>' + str(
                    complemento["DireccionConsignatarioODestinatario"]) + '</cex:DireccionConsignatarioODestinatario>'
                self.xml += '<cex:CodigoConsignatarioODestinatario>' + str(
                    complemento["CodigoConsignatarioODestinatario"]) + '</cex:CodigoConsignatarioODestinatario>'
                self.xml += '<cex:NombreComprador>' + str(complemento["NombreComprador"]) + '</cex:NombreComprador>'
                self.xml += '<cex:DireccionComprador>' + str(
                    complemento["DireccionComprador"]) + '</cex:DireccionComprador>'
                self.xml += '<cex:CodigoComprador>' + str(complemento["CodigoComprador"]) + '</cex:CodigoComprador>'
                self.xml += '<cex:OtraReferencia>' + str(complemento["OtraReferencia"]) + '</cex:OtraReferencia>'
                self.xml += '<cex:INCOTERM>' + str(complemento["INCOTERM"]) + '</cex:INCOTERM>'
                self.xml += '<cex:NombreExportador>' + str(complemento["NombreExportador"]) + '</cex:NombreExportador>'
                self.xml += '<cex:CodigoExportador>' + str(complemento["CodigoExportador"]) + '</cex:CodigoExportador>'
                self.xml += '</cex:Exportacion>'
            self.xml += '</dte:Complemento>'

        return self.xml


class complemento_especial():
    def __init__(self):
        self.xml = ''
        self.lista_complementos = []

    def agregar(self, retencion_isr, retencion_iva, total_menos_retenciones):
        self.lista_complementos.append({"RetencionISR": retencion_isr, "RetencionIVA": retencion_iva,
                                        "TotalMenosRetenciones": total_menos_retenciones})

    def to_xml(self):
        self.xml = ''
        if (len(self.lista_complementos) > 0):
            self.xml += '<dte:Complemento IDComplemento="text" NombreComplemento="GT_Complemento_Fac_Especial" URIComplemento="GT_Complemento_Fac_Especial.xsd">'

            for complemento in self.lista_complementos:
                self.xml += '<cfe:RetencionesFacturaEspecial Version="1" xsi:schemaLocation="http://www.sat.gob.gt/face2/ComplementoFacturaEspecial/0.1.0 C:\\Users\\Nadir\\Desktop\\Nov17\\GT_Complemento_Fac_Especial.xsd" xmlns:cfe="http://www.sat.gob.gt/face2/ComplementoFacturaEspecial/0.1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                self.xml += '<cfe:RetencionISR>' + str(complemento["RetencionISR"]) + '</cfe:RetencionISR>'
                self.xml += '<cfe:RetencionIVA>' + str(complemento["RetencionIVA"]) + '</cfe:RetencionIVA>'
                self.xml += '<cfe:TotalMenosRetenciones>' + str(
                    complemento["TotalMenosRetenciones"]) + '</cfe:TotalMenosRetenciones>'
                self.xml += '</cfe:RetencionesFacturaEspecial>'

            self.xml += '</dte:Complemento>'

        return self.xml


class complemento_cambiaria():
    def __init__(self):
        self.xml = ''
        self.lista_complementos = []

    def to_xml(self):
        self.xml = ''
        if (len(self.lista_complementos) > 0):
            self.xml += '<dte:Complemento IDComplemento="text" NombreComplemento="GT_Complemento_Cambiaria-0.1.0" URIComplemento="GT_Complemento_Cambiaria-0.1.0.xsd">'

            for complemento in self.lista_complementos:
                self.xml += '<cfc:AbonosFacturaCambiaria Version="1" xsi:schemaLocation="http://www.sat.gob.gt/dte/fel/CompCambiaria/0.1.0" xmlns:cfc="http://www.sat.gob.gt/dte/fel/CompCambiaria/0.1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                self.xml += '<cfc:Abono>'
                self.xml += '<cfc:NumeroAbono>' + str(complemento["numero_abono"]) + '</cfc:NumeroAbono>'
                self.xml += '<cfc:FechaVencimiento>' + str(complemento["fecha_vencimiento"]) + '</cfc:FechaVencimiento>'
                self.xml += '<cfc:MontoAbono>' + str(complemento["monto_abono"]) + '</cfc:MontoAbono>'
                self.xml += '</cfc:Abono>'
                self.xml += '</cfc:AbonosFacturaCambiaria>'

            self.xml += '</dte:Complemento>'

        return self.xml

    def agregar(self, num_abono, fec_vencimiento, mon_abono):
        self.lista_complementos.append(
            {"numero_abono": num_abono, "fecha_vencimiento": fec_vencimiento, "monto_abono": mon_abono})


class adenda:
    def __init__(self):
        self.nombre = ''
        self.valor = ''

    def set_nombre(self, n):
        self.nombre = n

    def set_valor(self, v):
        self.valor = v

    def to_xml(self):
        return '<' + self.nombre + '>' + self.valor + '</' + self.nombre + '>'


class total_impuesto:
    def __init__(self):
        self.nombre_corto = ''
        self.total_monto_impuesto = 0

    def set_nombre_corto(self, nc):
        self.nombre_corto = nc

    def set_total_monto_impuesto(self, t):
        self.total_monto_impuesto = t


class totales:
    def __init__(self):
        self.lista_total_impuesto = []
        self.gran_total = 0

    def set_gran_total(self, gran_tot):
        self.gran_total = gran_tot

    def set_total_impuestos(self, lista_total):
        self.lista_total_impuesto.append(lista_total)

    def to_xml(self):
        xml = ''
        xml += '<dte:Totales>'

        if (len(self.lista_total_impuesto) > 0):
            xml += '      <dte:TotalImpuestos>'
            for total_impuesto in self.lista_total_impuesto:
                xml += '      <dte:TotalImpuesto NombreCorto="' + total_impuesto.nombre_corto + '" TotalMontoImpuesto="' + str(
                    total_impuesto.total_monto_impuesto) + '"></dte:TotalImpuesto>'

            xml += '    </dte:TotalImpuestos>'
        xml += '    <dte:GranTotal>' + str(self.gran_total) + '</dte:GranTotal>'
        xml += '  </dte:Totales>'
        return xml


class impuesto:
    def __init__(self):
        self.MontoImpuesto = 0
        self.MontoGravable = 0
        self.CodigoUnidadGravable = 0
        self.NombreCorto = ''

    def set_monto_impuesto(self, monto_imp):
        self.MontoImpuesto = monto_imp

    def set_monto_gravable(self, monto_grav):
        self.MontoGravable = monto_grav

    def set_codigo_unidad_gravable(self, cod_unid_grav):
        self.CodigoUnidadGravable = cod_unid_grav

    def set_nombre_corto(self, nombre_corto_impuesto):
        self.NombreCorto = nombre_corto_impuesto

    def to_xml(self):
        return '<dte:Impuesto>' + '<dte:NombreCorto>' + self.NombreCorto + '</dte:NombreCorto>' + '<dte:CodigoUnidadGravable>' + str(
            self.CodigoUnidadGravable) + '</dte:CodigoUnidadGravable>' + '<dte:MontoGravable>' + str(
            self.MontoGravable) + '</dte:MontoGravable>' + '<dte:MontoImpuesto>' + str(
            self.MontoImpuesto) + '</dte:MontoImpuesto></dte:Impuesto>'


class item:
    def __init__(self):
        self.numero_linea = 0
        self.bien_o_servicio = ''
        self.Cantidad = 0
        self.UnidadMedida = 'UND'
        self.Descripcion = ''
        self.PrecioUnitario = 0
        self.Precio = 0
        self.Descuento = 0
        self.Impuestos = []
        self.Total = 0
        self.xml_plano = ''
        self.es_especial = False

    def set_impuesto(self, imp):
        self.Impuestos.append(imp)

    def set_numero_linea(self, numero):
        self.numero_linea = numero

    def set_bien_o_servicio(self, bien_servicio):
        self.bien_o_servicio = bien_servicio

    def set_cantidad(self, cant):
        self.Cantidad = cant

    def set_unidad_medida(self, unit):
        self.UnidadMedida = unit

    def set_descripcion(self, desc):
        self.Descripcion = desc

    def set_precio_unitario(self, precio_unitario):
        self.PrecioUnitario = precio_unitario

    def set_precio(self, precio):
        self.Precio = precio

    def set_descuento(self, descuento):
        self.Descuento = descuento

    def set_total(self, total):
        self.Total = total

    def set_es_especial(self, v):
        self.es_especial = v

    def to_xml(self):
        xml = ''
        xml += '<dte:Item BienOServicio="' + self.bien_o_servicio + '" NumeroLinea="' + str(self.numero_linea) + '">'
        xml += '<dte:Cantidad>' + str(self.Cantidad) + '</dte:Cantidad>'
        xml += '      <dte:UnidadMedida>' + self.UnidadMedida + '</dte:UnidadMedida>'
        xml += '      <dte:Descripcion>' + self.Descripcion + '</dte:Descripcion>'
        xml += '      <dte:PrecioUnitario> ' + str(self.PrecioUnitario) + ' </dte:PrecioUnitario>'
        xml += '      <dte:Precio>' + str(self.Precio) + '</dte:Precio>'
        xml += '      <dte:Descuento>' + str(self.Descuento) + '</dte:Descuento>'
        if (len(self.Impuestos) > 0):
            xml += '      <dte:Impuestos>'
            for impuesto_fel in self.Impuestos:
                xml += impuesto_fel.to_xml()
            xml += '      </dte:Impuestos>'

        xml += '      <dte:Total>' + str(self.Total) + '</dte:Total>'
        xml += '    </dte:Item>'
        return xml


class frase:
    def __init__(self):
        self.codigo = ''
        self.tipo = ''
        self.xml_plano = ''

    def to_xml(self):
        if (len(self.xml_plano) > 0):
            return '<dte:Frases>' + self.xml_plano + '</dte:Frases>'
        else:
            return ""

    # def set_frase(self, codigo_frase, tipo_frase):
    #    self.xml_plano += '<dte:Frase CodigoEscenario="'+ codigo_frase +'" TipoFrase="'+tipo_frase+'"></dte:Frase>'

    def set_frase(self, codigo_frase, tipo_frase, numero_resolucion='', fecha_resolucion=''):
        texto_numero_resolucion = ''
        texto_fecha_resolucion = ''

        if (len(numero_resolucion) > 0):
            texto_numero_resolucion = ' NumeroResolucion="' + numero_resolucion + '" '

        if (len(fecha_resolucion) > 0):
            texto_fecha_resolucion = ' FechaResolucion="' + fecha_resolucion + '" '
        #revisar si se puede utilizar lal inea ya que es extra
        self.xml_plano += '<dte:Frase CodigoEscenario="' + codigo_frase + '" TipoFrase="' + tipo_frase + '" ' + texto_numero_resolucion + texto_fecha_resolucion + '></dte:Frase>'


class fel_dte:
    def __init__(self):
        self.clave_unica = ''
        self.emisor = ContapEmisor.emisor()
        self.receptor = ContapReceptor.receptor()
        self.frase_fel = frase()
        self.totales_fel = totales()
        self.xml_plano = ''
        self.xml_firmado = ''
        self.xml_certificado = ''
        self.datos_emisor = ''
        self.datos_generales = ''
        self.item_list = []
        self.lista_adendas = []
        self.lista_complementos = []
        #  self.GTDocumento = r'<dte:GTDocumento xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:dte="http://www.sat.gob.gt/dte/fel/0.2.0" xmlns:n1="http://www.altova.com/samplexml/other-namespace" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" Version="0.1" xsi:schemaLocation="http://www.sat.gob.gt/dte/fel/0.1.0 C:\Users\Nadir\Desktop\SAT_FEL_FINAL_V1\Esquemas\GT_Documento-0.1.0.xsd">'
        self.GTDocumento = r'<dte:GTDocumento Version="0.1" xmlns:cex="http://www.sat.gob.gt/face2/ComplementoExportaciones/0.1.0" xmlns:cfc="http://www.sat.gob.gt/dte/fel/CompCambiaria/0.1.0" xmlns:cfe="http://www.sat.gob.gt/face2/ComplementoFacturaEspecial/0.1.0" xmlns:cno="http://www.sat.gob.gt/face2/ComplementoReferenciaNota/0.1.0" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:dte="http://www.sat.gob.gt/dte/fel/0.2.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sat.gob.gt/dte/fel/0.2.0 GT_Documento-0.2.0.xsd">'
        self.SAT = '<dte:SAT ClaseDocumento="dte">'
        self.exportacion = ''
        self.acceso = ''
        self.tipo_personeria = ''
        self.tipo_especial = ''
        self.codigo_moneda = ''
        self.fecha_hora_emision = ''
        self.tipo_dte = ''

    def anular(self, fecha_hora_anulacion, nit_emisor, fecha_emision_documento_anular, id_receptor,
               numero_documento_anular, motivo_anulacion, key_certify, key_sign, user, vat, email):
        self.xml_plano = ''
        self.xml_plano += '<?xml version="1.0" encoding="UTF-8"?>'
        self.xml_plano += '<dte:GTAnulacionDocumento Version="0.1" xsi:schemaLocation="http://www.sat.gob.gt/dte/fel/0.1.0" xmlns:n1="http://www.altova.com/samplexml/other-namespace" xmlns:dte="http://www.sat.gob.gt/dte/fel/0.1.0" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        self.xml_plano += '<dte:SAT>'
        self.xml_plano += '<dte:AnulacionDTE ID="DatosCertificados">'
        self.xml_plano += '<dte:DatosGenerales FechaHoraAnulacion="' + fecha_hora_anulacion + '" ID="DatosAnulacion" NITEmisor="' + nit_emisor + '" FechaEmisionDocumentoAnular="' + fecha_emision_documento_anular + '" IDReceptor="' + id_receptor + '" NumeroDocumentoAAnular="' + numero_documento_anular + '" MotivoAnulacion="' + motivo_anulacion + '"/>'
        self.xml_plano += '</dte:AnulacionDTE>'
        self.xml_plano += '</dte:SAT>'
        self.xml_plano += '</dte:GTAnulacionDocumento>'
        print('*********************')
        print(self.xml_plano)
        print('*********************')
        self.fel_firma_response = self.firmar_xml(self.xml_plano, "S", key_sign, user)
        #print(self.fel_firma_response, 'respuesta de firma aqui')
        #if (self.fel_firma_response["resultado"]):
        #    self.xml_firmado = self.fel_firma_response["archivo"]
        self.fel_certificacion_response = self.certificar_xml(self.xml_plano, "S", token)
        print(self.fel_certificacion_response, 'respuesta de certificacion aqui')
        if (self.fel_certificacion_response["resultado"]):
            self.certificacion_fel = {"resultado": True, "fecha": self.fel_certificacion_response["fecha"],
                                          "uuid": self.fel_certificacion_response["uuid"],
                                          "serie": self.fel_certificacion_response["serie"],
                                          "numero": self.fel_certificacion_response["numero"],
                                          "xml_plano": self.xml_plano,
                                          # "xml_firmado": self.xml_firmado,
                                          "xml_certificado": self.fel_certificacion_response["xml_certificado"],
                                          "descripcion_alertas_infile": self.fel_certificacion_response[
                                              "descripcion_alertas_infile"]}
        else:
            self.certificacion_fel = self.fel_certificacion_response
            self.certificacion_fel["xml_plano"] = self.xml_plano

        #revisar el else si se va a tomar en cuenta
        # else:
        #     self.certificacion_fel = {
        #         "resultado": False, "descripcion": "XML no pudo ser certificado, reintente",
        #         "xml_plano": self.xml_plano, "sign_response": self.fel_firma_response
        #     }

        return self.certificacion_fel

    def certificar(self, token):
        self.xml_plano += self.GTDocumento
        self.xml_plano += self.SAT
        self.xml_plano += '<dte:DTE ID="DatosCertificados">'
        self.xml_plano += '<dte:DatosEmision ID="DatosEmision">'
        self.xml_plano += self.xml_datos_generales()  # self.datos_generales  #hay que ver como se mete el numero de acceso
        self.xml_plano += self.datos_emisor
        self.xml_plano += self.emisor.to_xml()
        self.xml_plano += self.receptor.to_xml()

        self.xml_plano += self.frase_fel.to_xml()

        self.certificacion_fel = {}
        if (len(self.item_list) > 0):
            self.xml_plano += '<dte:Items>'
            for item in self.item_list:
                self.xml_plano += item.to_xml()
            self.xml_plano += '</dte:Items>'

        self.xml_plano += self.totales_fel.to_xml()
        self.xml_plano += self.xml_complementos()
        self.xml_plano += '</dte:DatosEmision>'
        self.xml_plano += '</dte:DTE>'

        if (len(self.lista_adendas) > 0):
            self.xml_plano += '<dte:Adenda>'
            for adenda in self.lista_adendas:
                self.xml_plano += adenda.to_xml()
            self.xml_plano += '</dte:Adenda>'

        self.xml_plano += '</dte:SAT>'
        self.xml_plano += '</dte:GTDocumento>'
        print('*********************')
        print(self.xml_plano)
        print('*********************')

        #_logger.info('*********************')
        #_logger.info(self.xml_plano, 'XML PLANO')
        #_logger.info('*********************')
        print("Antes de Firmar")
        self.fel_firma_response = self.firmar_xml(self.xml_plano, "N", token)
        if (self.fel_firma_response["resultado"]):
            self.xml_firmado = self.fel_firma_response["archivo"]

        self.fel_certificacion_response = self.certificar_xml(self.xml_plano, "N",
                                                                  token)
        if (self.fel_certificacion_response["resultado"]):
            self.certificacion_fel = {"resultado": True, "fecha": self.fel_certificacion_response["fecha"],
                                          "uuid": self.fel_certificacion_response["uuid"],
                                          "serie": self.fel_certificacion_response["serie"],
                                          "numero": self.fel_certificacion_response["numero"],
                                          "xml_plano": self.xml_plano,
                                          # "xml_firmado": self.xml_firmado,
                                          "xml_certificado": self.fel_certificacion_response["xml_certificado"],
                                          "descripcion_alertas_infile": self.fel_certificacion_response[
                                              "descripcion_alertas_infile"]}
        else:
            self.certificacion_fel = self.fel_certificacion_response
            self.certificacion_fel["xml_plano"] = self.xml_plano
        # else:
        #     self.certificacion_fel = {
        #         "resultado": False, "descripcion": "XML no pudo ser certificado, reintente",
        #         "xml_plano": self.xml_plano, "sign_response": self.fel_firma_response
        #     }

        return self.certificacion_fel

    def agregar_complemento(self, complemento):
        self.lista_complementos.append(complemento)

    def set_tipo_especial(self, tipo_esp):
        self.receptor.set_especial(tipo_esp)

    def set_exportacion(self, exp):
        self.exportacion = exp

    def set_acceso(self, acceso):
        self.acceso = acceso

    def set_tipo_personeria(self, tipo_personeria):
        self.tipo_personeria = tipo_personeria

    def set_clave_unica(self, clave):
        self.clave_unica = clave

    def xml_complementos(self):
        xml_complemento = ''
        if (len(self.lista_complementos) > 0):
            xml_complemento += '<dte:Complementos>'
            for complemento in self.lista_complementos:
                xml_complemento += complemento.to_xml()
            xml_complemento += '</dte:Complementos>'
        return xml_complemento

    def generar_expo(self):
        print("EN LA EXPORTACION .................................." + str(len(self.exportacion)))
        retorno = ''
        if (len(self.exportacion) > 0):
            retorno = 'Exp="' + self.exportacion + '"'
        return retorno

    def generar_acceso(self):
        retorno = ''
        if (len(self.acceso) > 0):
            retorno = ' NumeroAcceso="' + self.acceso + '"'
        return retorno

    def generar_tipo_personeria(self):
        retorno = ''
        if (len(self.tipo_personeria) > 0):
            retorno = ' TipoPersoneria="' + self.tipo_personeria + '"'
        return retorno

    def set_datos_generales(self, codigo_moneda, fecha_hora_emision, tipo_dte):
        self.codigo_moneda = codigo_moneda
        self.fecha_hora_emision = fecha_hora_emision
        self.tipo_dte = tipo_dte
        # self.datos_generales = '<dte:DatosGenerales CodigoMoneda="'+ codigo_moneda + self.generar_expo() + '" FechaHoraEmision="'+ fecha_hora_emision +  self.generar_acceso() +'" Tipo="'+ tipo_dte +'"></dte:DatosGenerales>'

    def xml_datos_generales(self):
        self.datos_generales = '<dte:DatosGenerales CodigoMoneda="' + self.codigo_moneda + '" ' + self.generar_expo() + ' FechaHoraEmision="' + self.fecha_hora_emision + '"' + self.generar_acceso() + ' Tipo="' + self.tipo_dte + '"' + self.generar_tipo_personeria() + '></dte:DatosGenerales>'
        return self.datos_generales

    def set_datos_emisor(self, emi):
        self.emisor = emi

    def set_datos_receptor(self, rec):
        self.receptor = rec

    def agregar_adenda(self, fel_adenda):
        self.lista_adendas.append(fel_adenda)

    def agregar_item(self, fel_item):
        self.item_list.append(fel_item)

    def agregar_totales(self, fel_totales):
        self.totales_fel = fel_totales

    def access_number(self):
        counter_access_number = self.env.company.counter_access_number
        if counter_access_number < 9999999:
            access_number = counter_access_number + 1
            self.env.company.counter_access_number += 1
            return access_number
        else:
            raise ValueError('El numero de accesso de contingencia es igual a 9999999.')

    #def firmar_xml(self, xml_plano, anulacion, key, user):
    def firmar_xml(self, xml_plano, anulacion, token):
        print("Entro")
        UrlFirma = 'https://pruebas-contap-279823.appspot.com/firmarEmitirFactura'

        #_logger.warning(xml_plano, 'XML PLANO')

        b = xml_plano.encode("UTF-8")
        e = base64.b64encode(b)
        xml_64 = e.decode("UTF-8")

        data = xml_plano
        #buscar el token como parametro
        headers = {
            'Token':token,
            'Content-Type': 'application/xml; charset=utf-8'
        }

        #  CAMBIO PARA CONTINGENCIAS
        access_number = False
        r = False
        print("----------------------------------------------------------")
        print(data)
        print("----------------------------------------------------------")
        try:
            r = requests.post(url=UrlFirma, data=data, headers=headers)
            print("------------------------------")
            print(r.text)
            print("------------------------------")
        except requests.exceptions.Timeout:
            access_number = self.access_number()

        if r.status_code in [522, 524]:
            access_number = self.access_number()
        #  CAMBIO PARA CONTINGENCIAS

        # raise ValueError(r.text, 'RESPUESTA DESDE INFILE')
        print(r, 'respuesta sign gneral')
        _logger.warning(r.json(), 'RESPUESTA SIGN EN TEXTO')
        print(r.json(), 'respuesta sign en text')
        fel_firma_response = r.json()
        if access_number:
            fel_firma_response['access_number'] = access_number
        return fel_firma_response

    def certificar_xml(self, xml_firmado, anulacion, token):

        if anulacion != "S":
            url_cert = 'https://pruebas-contap-279823.appspot.com/signEmitterXml'
        else:
            url_cert = 'https://pruebas-contap-279823.appspot.com/anularDte'


        data = xml_firmado
        #buscar el token como parametro
        headers = {
            'Token': token,
            'Content-Type': 'application/xml; charset=utf-8'
        }

        #  CAMBIO PARA CONTINGENCIAS
        access_number = False
        r = False

        try:
            r = requests.post(url=url_cert, data=json.dumps(data), headers=headers)
        except requests.exceptions.Timeout:
            access_number = self.access_number()

        if r.status_code in [522, 524]:
            access_number = self.access_number()
        #  CAMBIO PARA CONTINGENCIAS

        print(r, 'respuesta cert gneral')
        # raise ValueError(r.text, 'RESPUESTA DESDE INFILE AL CERT')
        print(r.text, 'respuesta cert en text')
        fel_certificacion_response = r.json()
        #  CAMBIO PARA CONTINGENCIAS
        if access_number:
            fel_certificacion_response['access_number'] = access_number
        return fel_certificacion_response
