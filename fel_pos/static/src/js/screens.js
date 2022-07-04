odoo.define('fel_pos.screens', ['point_of_sale.screens', 'web.rpc'], function(require)
{
	"use strict";
	const screens = require('point_of_sale.screens');
	const rpc = require('web.rpc');

	screens.PaymentScreenWidget = screens.PaymentScreenWidget.include({

        finalize_validation: function () {
            let self = this;
            let order = this.pos.get_order();

            if (order.is_paid_with_cash() && this.pos.config.iface_cashdrawer) {
                this.pos.proxy.open_cashbox();
            }

            order.initialize_validation_date();
            order.finalized = true;

            if (order.is_to_invoice()) {
                let invoiced = this.pos.push_and_invoice_order(order);
                this.invoicing = true;
                invoiced.fail(this._handleFailedPushForInvoice.bind(this, order, false));

                invoiced.done(function(){
                    self.invoicing = false;

                    // Llamada a renderizado del ticket detenida por 5 segundos
                    // Mejora hecha el 02.11.2021
                    // Necesaria para uso de ticket  FEL PoS
                    // Solucionando el fallo de asincronía del código js
                    order.get_invoice().done( function( result ) {
                        order.invoice_id = result;
                    }).then( function( ) {
                        self.gui.show_screen('receipt');
                    });
                });
            } else {
                // Llamada a renderizado del ticket detenida por 5 segundos'
                // Mejora hecha el 02.11.2021
                // Necesaria para uso de ticket  FEL PoS
                // Solucionando el fallo de asincronía del código js
                Promise.all([this.pos.push_order(order)])
                .then(function () {
                    order.get_invoice().done( function( result ) {
                        order.invoice_id = result;
                    }).then( function( ) {
                        self.gui.show_screen('receipt');
                    });
                })
            }
        },
	});
});




