odoo.define('fel_pos.models', ['point_of_sale.models', 'web.rpc'], function(require)
{
	"use strict";
	const models = require('point_of_sale.models');
	const rpc = require('web.rpc');

    models.load_fields("pos.order", 'invoice_id');
    //D:\odoo-15.0\addons\point_of_sale\static\src\js\models.js L#2819
    let order_model_super = models.Order.prototype;
	models.Order = models.Order.extend({

	    initialize: function(attributes,options){
            let init = order_model_super.initialize.apply(this, arguments);

            init.invoice_id = {
                fel_uuid: 'De momento, sin datos FEL',
                fel_serie: 'De momento, sin datos FEL',
                fel_number: 'De momento, sin datos FEL',
                fel_date: 'De momento, sin datos FEL',
            };
            return init
        },

        //  Mejora hecha el 30.10.2021
        // Actualización del 03.11.2021
        // Necesaria para uso de ticket  FEL PoS
        // Solucionando el fallo de asincronía del código js
	    get_invoice: function () {
            let self = this;
            let order = this.pos.get_order();
            console.log('Order', order);
            console.log('Order THIS', this);
            let order_ref = order.name;
            let fel_values = rpc.query({
                model: 'pos.order',
                method: 'get_invoice_pos_order',
                args: [order_ref],
            },{
                timeout: 3000,
                shadow: true
            }).then(function (result) {
                console.log('resultado', result);
                if ( result ) {
                    return result;
                } else {
                    return {
                        fel_uuid: 'No ha sido posible obtener los datos FEL',
                        fel_serie: 'No ha sido posible obtener los datos FEL',
                        fel_number: 'No ha sido posible obtener los datos FEL',
                        fel_date: 'No ha sido posible obtener los datos FEL',
                    }
                };
            });
            return fel_values;
        },

        export_for_printing: function () {
            //  https://stackoverflow.com/questions/57653402/how-to-prevent-asynchronous-execution-in-odoo-10
            //
            // Mejora hecha el 30.10.2021
            // Actualización del 03.11.2021
            // Necesaria para uso de ticket  FEL PoS
            // Solucionando el fallo de asincronía del código js
            let self = this;
            let client  = this.get('client');
            let receipt = order_model_super.export_for_printing.bind(this)();
            let default_fel_values = {
                fel_uuid: 'De momento, sin datos FEL',
                fel_serie: 'De momento, sin datos FEL',
                fel_number: 'De momento, sin datos FEL',
                fel_date: 'De momento, sin datos FEL',
            }
            receipt = _.extend(receipt, {
                invoice_id: default_fel_values,
                client: {
                    name: client ? client.name : '',
                    vat: client ? client.vat : 'CF',
                }
            });

            console.log('ULTIMO TICKET', receipt);
            return receipt;
            // No funcionaba, pues otra herencia al mismo metodo es llamada y el valor de receipt es indefinido.
            // Retorna un valor para el método antes que esta herencia concluya.
        },
	});
});
