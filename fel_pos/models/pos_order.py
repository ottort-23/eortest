# -*- coding: utf-8 -*-

import logging
import psycopg2

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def create_from_ui(self, orders):
        """Mejora hecha el 01.09.2021
           Necesaria para uso de FEL PoS
        """
        # Keep only new orders
        submitted_references = [o['data']['name'] for o in orders]
        pos_order = self.search([('pos_reference', 'in', submitted_references)])
        existing_orders = pos_order.read(['pos_reference'])
        existing_references = set([o['pos_reference'] for o in existing_orders])
        orders_to_save = [o for o in orders if o['data']['name'] not in existing_references]
        order_ids = []

        for tmp_order in orders_to_save:
            """Actualización para indicar que se necesita imprimir un reporte de factura.
            """
            tmp_order['to_invoice'] = True
            tmp_order['data']['to_invoice'] = True
            """----------------Fin Actualización-------------------"""
            to_invoice = tmp_order['to_invoice']
            order = tmp_order['data']
            if to_invoice:
                self._match_payment_to_invoice(order)
            pos_order = self._process_order(order)
            order_ids.append(pos_order.id)

            try:
                pos_order.action_pos_order_paid()
            except psycopg2.DatabaseError:
                # do not hide transactional errors, the order(s) won't be saved!
                raise
            except Exception as e:
                _logger.error('Could not fully process the POS Order: %s', tools.ustr(e), exc_info=True)

            if to_invoice:
                pos_order.action_pos_order_invoice()
                """Actualización del 02.09.2021
                    Mejora para agregar contexto del tipo de documento y según esto se emitan documentos con FEL. 
                """
                pos_order.invoice_id.sudo().with_context(
                    force_company=self.env.user.company_id.id, pos_picking_id=pos_order.picking_id,
                    default_type=pos_order.invoice_id.type,
                ).action_invoice_open()
                """-------Fin de actualización en esta sección---------"""
                pos_order.account_move = pos_order.invoice_id.move_id
        return order_ids

    def _prepare_invoice(self):
        """Mejora hecha el 01.09.2021
            Necesaria para uso de FEL PoS
        """
        vals = super(PosOrder, self)._prepare_invoice()
        """Actualización para agregar eL tipo de documento de la secuencia del diario del PoS, 
            la indicación que el documento es creado desde el PoS.
        """
        vals.update({'doc_type': self.session_id.config_id.invoice_journal_id.doc_type, 'pos_inv': True})
        """----------------Fin Actualización-------------------"""
        return vals

    def _action_create_invoice_line(self, line=False, invoice_id=False):
        """Mejora hecha el 01.09.2021
            Necesaria para uso de FEL PoS
        """
        InvoiceLine = self.env['account.invoice.line']
        inv_name = line.product_id.name_get()[0][1]
        inv_line = {
            'invoice_id': invoice_id,
            'product_id': line.product_id.id,
            'quantity': line.qty if self.amount_total >= 0 else -line.qty,
            'account_analytic_id': self._prepare_analytic_account(line),
            'name': inv_name,
        }
        # Oldlin trick
        invoice_line = InvoiceLine.sudo().new(inv_line)
        invoice_line._onchange_product_id()
        """Actualización para cambiar la obtención de impuestos para las líneas de los documentos contables.
            El uso normal hace lo siguiente: line.tax_ids_after_fiscal_position.filtered......
            Lo cual no controla los impuestos obligatorios para las emisiones FEL (IVA). 
            La mejora consiste en obtener los impuestos que tiene el producto de la línea a facturar.
        """
        invoice_line.invoice_line_tax_ids = [
            (6, False, line.product_id.taxes_id.filtered(lambda t: t.company_id.id == line.order_id.company_id.id).ids)]
        """----------------Fin Actualización-------------------"""
        # We convert a new id object back to a dictionary to write to
        # bridge between old and new api
        inv_line = invoice_line._convert_to_write({name: invoice_line[name] for name in invoice_line._cache})
        inv_line.update(price_unit=line.price_unit, discount=line.discount)
        return InvoiceLine.sudo().create(inv_line)

    def _create_invoice(self):
        """Mejora hecha el 02.09.2021
            Necesaria para uso de FEL PoS
        """
        self.ensure_one()
        Invoice = self.env['account.invoice']
        # Force company for all SUPERUSER_ID action
        local_context = dict(self.env.context, force_company=self.company_id.id, company_id=self.company_id.id)
        if self.invoice_id:
            return self.invoice_id

        if not self.partner_id:
            raise UserError(_('Please provide a partner for the sale.'))

        invoice = Invoice.new(self._prepare_invoice())
        invoice._onchange_partner_id()
        invoice.fiscal_position_id = self.fiscal_position_id

        """Actualización del 02.09.2021
             Mejora para agregar la fecha de creación y la fecha de vencimiento del doc a emitir.
        """
        date_invoice = invoice.date_invoice
        if not date_invoice:
            date_invoice = fields.Date.context_today(self)
        if invoice.payment_term_id:
            pterm = invoice.payment_term_id
            pterm_list = \
                pterm.with_context(currency_id=self.company_id.currency_id.id).compute(value=1, date_ref=date_invoice)[
                    0]
            date_due = max(line[0] for line in pterm_list)
        else:
            date_due = invoice.date_invoice
        invoice.date_invoice = date_invoice
        invoice.date_due = date_due
        """----------------Fin Actualización-------------------"""

        inv = invoice._convert_to_write({name: invoice[name] for name in invoice._cache})
        new_invoice = Invoice.with_context(local_context).sudo().create(inv)
        message = _(
            "This invoice has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (
                      self.id, self.name)
        new_invoice.message_post(body=message)
        self.write({'invoice_id': new_invoice.id, 'state': 'invoiced'})

        for line in self.lines:
            self.with_context(local_context)._action_create_invoice_line(line, new_invoice.id)

        new_invoice.with_context(local_context).sudo().compute_taxes()
        self.sudo().write({'state': 'invoiced'})
        return new_invoice

    @api.model
    def get_invoice_pos_order(self, order_ref):
        """Mejora del 15.09.2021
            Actualización del 03.11.2021
            Necesaria para uso de FEL PoS Ticket.
            Obtiene el pedido PoS por medio del nombre y a su vez, retorna los valores de emisión FEL de la
            factura unida a dicho pedido.
            En caso de no obtenerse el pedido, devuelve un dict vacío.
        """
        pos_order = self
        try:
            pos_order = self.search([('pos_reference', '=', order_ref)])
        except Exception as e:
            _logger.error('Hubo un error obtener el pedido de PoS %s: %s', (tools.ustr(order_ref) or '', tools.ustr(e)))

        res = pos_order.invoice_id.read(
            ['fel_uuid', 'fel_serie', 'fel_number', 'fel_date', 'fel_num_acceso', 'doc_type']) if pos_order else False
        values = res and res[0] or {}
        return values
