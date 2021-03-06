# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Update_product_template(models.Model):
    _inherit = "product.template"

    clase = fields.Selection([('equipo','Equipo'),('agricola','Producto Agricola'),('logistica','Operacion Logistica')],string="Clase")
    #formula = fields.One2many('product.product.purpose','name')
    #applications = fields.Many2many('product.product.application')
    summary = fields.Char(string="summary")
    dosis_mz = fields.Integer('Dosis_mz')
    dosis_barrel = fields.Integer('Dosis_barrel')
    dosis_dump = fields.Integer('Dosis_dump')
    liquid_tank = fields.Char('Tanque de Agua')
    work_pesion = fields.Char('Pesion Trabajo')
    air_chamber = fields.Char('Cap. Camara de Aire')
    drums = fields.Char('Bateria')
    vol_aspersion = fields.Char('Vol. Aspersión')
    duration = fields.Char('Duracion')
    dimensions = fields.Char('Dimensiones')
    motor = fields.Char('Motor')
    pump = fields.Char('Bomba')
    fan = fields.Char('Ventilador')
    dis_aspersion = fields.Char('Dist. Aspersion')
    cap_desc = fields.Char('Cap. Descarga')
    diaphragms = fields.Char('Diagragmas')
    membranes = fields.Char('Membranas')
    piston = fields.Char('Piston')
    pressure = fields.Char('Presión')
    maximum_height = fields.Char('Altura Maxima')
    maximum_suction = fields.Char('Succion Max.')
    pump_type = fields.Char('Tipo de Bomba')
    diam_suction_discharge = fields.Char('Diám. De Succión y Descarga')
    num_impellers = fields.Char('Numero de Impulsores')
    volts = fields.Char('Volts')
    metal_rim_measurements = fields.Char('Medidas de llanta de metal')
    external_tire_measurement = fields.Char('Medida entre llantas externas')
    plow_width = fields.Char('Anchura del arador')
    plow_width_2 = fields.Char('Anchura del arado')
    set_blades = fields.Char('Set de Cuchillas')
    diam_spikes = fields.Char('Diam. de puas')
    plow_depth = fields.Char('Profundidad de Arado')
    plow_speed = fields.Char('Velocidad de Arado')
    transmission = fields.Char('Transmision')
    tire = fields.Char('Llanta')
    handle = fields.Char('Maneral')
    handle_barr = fields.Char('Barra Maneral')
    entry = fields.Char('Entrada')
    drained_outlet = fields.Char('Salida Drenado')
    for_tractor = fields.Char('Para Tractor')
    turbine = fields.Char('Turbina')
    nozzle = fields.Char('Boquillas')
    spray_range = fields.Char('Alcance Aspersión')
    fan_diam = fields.Char('Diam. Ventilador')
    arrow = fields.Char('Flecha')
    dimensions_2 = fields.Char('Dimensiones secundarias')
    extra_deposit = fields.Char('Depósito Extra')
    control = fields.Char('Control')
    rim_type = fields.Char('Tipo de Llanta')
    speed = fields.Char('Velocidad')
    tube = fields.Char('Tubo')
    blades = fields.Char('Cuchillas')
    maximum_speed = fields.Char('Maxima Velocidad')
    vol_air_max = fields.Char('Vol. Aire Max')
    transmission_tube_diam = fields.Char('Diám. Tubo de Transmisión')
    paso = fields.Char('Paso')
    cut_diameter = fields.Char('Diametro de Corte')
    eslab = fields.Char('Eslabones')
    bar = fields.Char('Barra')
