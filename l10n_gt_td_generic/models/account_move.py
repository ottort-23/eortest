# -*- coding: utf-8 -*-

from collections import defaultdict
from num2words import num2words
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import fields, api, models, _
from odoo.exceptions import UserError, AccessError
from odoo.tools import float_compare, format_date, get_lang


class AccountMoveInherited(models.Model):
    _inherit = "account.move"

    @api.model
    def convert_amount_in_words(self, amount, language, currency, lang):
        """
        Método para convertir un valor numérico en letras.
        :param amount: int or float value
        :param language: str value to language response
        :param currency: account.currency object
        :param lang: str value to localization
        :return: str amount in words
        """
        list_lang = [['en', 'en_US'], ['en', 'en_AU'], ['en', 'en_GB'], ['en', 'en_IN'],
                     ['fr', 'fr_BE'], ['fr', 'fr_CA'], ['fr', 'fr_CH'], ['fr', 'fr_FR'],
                     ['es', 'es_ES'], ['es', 'es_AR'], ['es', 'es_BO'], ['es', 'es_CL'], ['es', 'es_CO'],
                     ['es', 'es_CR'], ['es', 'es_DO'],
                     ['es', 'es_EC'], ['es', 'es_GT'], ['es', 'es_MX'], ['es', 'es_PA'], ['es', 'es_PE'],
                     ['es', 'es_PY'], ['es', 'es_UY'], ['es', 'es_VE'],
                     ['lt', 'lt_LT'], ['lv', 'lv_LV'], ['no', 'nb_NO'], ['pl', 'pl_PL'], ['ru', 'ru_RU'],
                     ['dk', 'da_DK'], ['pt_BR', 'pt_BR'], ['de', 'de_DE'], ['de', 'de_CH'],
                     ['ar', 'ar_SY'], ['it', 'it_IT'], ['he', 'he_IL'], ['id', 'id_ID'], ['tr', 'tr_TR'],
                     ['nl', 'nl_NL'], ['nl', 'nl_BE'], ['uk', 'uk_UA'], ['sl', 'sl_SI'], ['vi_VN', 'vi_VN']]

        #     ['th','th_TH'],['cz','cs_CZ']
        cnt = 0
        for rec in list_lang[cnt:len(list_lang)]:
            if rec[1] == lang:
                language = rec[0]
            cnt += 1

        amount_str = str('{:2f}'.format(amount))
        amount_str_splt = amount_str.split('.')
        before_point_value = amount_str_splt[0]
        after_point_value = amount_str_splt[1][:2]

        before_amount_words = num2words(int(before_point_value), lang=language)
        after_amount_words = num2words(int(after_point_value), lang=language)

        amount = before_amount_words

        if currency and currency.currency_unit_label:
            amount += ' ' + currency.currency_unit_label

        if currency and currency.amount_separator:
            amount += ' ' + currency.amount_separator

        if int(after_point_value) > 0:
            amount += ' con ' + str(after_point_value) + '/100.'
        else:
            amount += ' exactos.'

        return amount

    @api.depends('amount_total')
    def compute_amount_word(self):
        """Método para manejar la conversión a letras de un monto de pago."""
        for record in self:
            amount = record.convert_amount_in_words(record.amount_total, 'es',
                                                    record.currency_id, record.partner_id.lang)
            record.amount_in_words = amount.capitalize()

    # campo para calculo de fecha de pago segun configuracion de dias
    @api.depends('invoice_date', 'invoice_date_due')
    def _compute_invoice_date(self):
        """
        Actualización del 21.05.2021
        Mejora a código de computación de los campos:
            credit_days
            payment_date
        Reducción de código y mejora en la legibilidad del mismo.
        Aparte solución a fallo al no ingresar una fecha de factura de forma manual,
        ya que esto impedia calcular los dias credito y la fecha de pago.
        :return:
        """
        for record in self:
            day = record.invoice_date or fields.Date.today()
            record.credit_days = (record.invoice_date_due - day).days if record.invoice_date_due else 0
            payment_day = record.env.company.payment_day or 4
            if payment_day - day.weekday() <= 0:
                date = day - timedelta(days=day.weekday()) + timedelta(days=payment_day, weeks=1)
            else:
                date = day - timedelta(days=day.weekday()) + timedelta(days=payment_day)
            record.payment_date = date.strftime("%d/%m/%Y")

    #  Campos para busqueda por NIT y Razon Social en Contabilidad, Ventas y CRM
    nit = fields.Char(related="partner_id.vat", string="NIT")
    legal_name = fields.Char(related="partner_id.legal_name", string="Razón Social")
    amount_in_words = fields.Char(compute='compute_amount_word', string='Monto en letras facturas')
    print_to_report = fields.Boolean(string="Mostrar en reporte", default=True)
    name = fields.Char(tracking=3)
    ref = fields.Char(tracking=3)
    date = fields.Date(tracking=3)
    journal_id = fields.Many2one(tracking=3)
    currency_id = fields.Many2one(tracking=3)
    state = fields.Selection(tracking=3)
    partner_id = fields.Many2one(tracking=3)
    credit_days = fields.Integer(store=True, compute='_compute_invoice_date', string="Días crédito")

    invoice_doc_type = fields.Many2one(
        'l10n_latam.document.type', string='Tipo Documento', copy=False, index=True,
    )  # states={'posted': [('readonly', True)]}
    invoice_doc_serie = fields.Char("Serie", copy=False)  # , states={'posted': [('readonly', True)]}
    invoice_doc_number = fields.Char("Numero", copy=False)  # , states={'posted': [('readonly', True)]}
    invoice_ref = fields.Char(string="Referencia", compute="_set_reference")

    # Necesario para Coversion segun tasa de cambio
    amount_total_signed_2 = fields.Monetary(string="Total segun Tasa de Cambio", readonly=True)
    rate_invoice = fields.Float(string='Tasa de Cambio', readonly=True, digits=(1, 6), compute='_compute_rate_invoice')

    # campo para calculo de fecha de pago segun configuracion de dias
    payment_date = fields.Char(
        compute='_compute_invoice_date',
        help='Aquí va la fecha de la entrega del pago del pedido de compra, '
             'de formma estandar se traslada al siguiente viernes de la fecha de confirmacion de la compra.',
        string="Fecha Entrega de Pago"
    )

    @api.onchange('invoice_date', 'highest_name', 'company_id')
    def _onchange_invoice_date(self):
        """Sobrescritura del método genérico para modificar el funcionamiento de asignación
            de una fecha contable sólo cuando los tipos de
            documentos son: Z1. ('entry', 'out_invoice', 'out_refund', 'out_receipt'),
            ya que en este caso deben ser valores iguales los de los campos
            ´invoice_date´ y ´date´. Z2. Si los documentos son de tipo de proveedor,
            las fechas contables pueden ser distintas, máximo mayores a 2 meses con respecto a la fecha de la factura.
            A1. Tener en cuenta que en Odoo15, el funcionamiento normal
            es que la fecha contable siempre depende de la fecha de la factura.
            Por tanto, para obtener o actualizar la fecha contable según los lineamientos anteriores (Z1 Y Z2),
            se hará conforme a lo anterior indicado (A1).
        """
        if self.invoice_date:
            if not self.invoice_payment_term_id and (
                    not self.invoice_date_due or self.invoice_date_due < self.invoice_date):
                self.invoice_date_due = self.invoice_date

            accounting_date = self.invoice_date

            if not self.is_sale_document(include_receipts=True) and not self.date:
                accounting_date = self._get_accounting_date(self.invoice_date, self._affect_tax_report())

            delta = relativedelta(self.date, self.invoice_date)
            res_months = delta.months + (delta.years * 12) or delta.days

            if accounting_date != self.date and self.move_type in ('entry', 'out_invoice', 'out_refund', 'out_receipt'):
                self.date = accounting_date
                self._onchange_currency()
            elif self.move_type in ('in_invoice', 'in_refund', 'in_receipt') and (res_months < 0 or res_months > 2):
                raise UserError('Sólo es posible tener una diferencia '
                                'de 2 meses entre la fecha contable y la fecha de la factura.'
                                'La fecha contable núnca puede ser mayor a la fecha de la factura.')
            else:
                self._onchange_recompute_dynamic_lines()

    def action_post(self):
        """Sobrescritura del método para asignar una fecha de documento según haya o no valores en los campos
            ´invoice_date´ y ´date´. Si no hay valores en dichos campos, colocar la fecha de hoy, en otro caso,
            colocar el valor del campo date´ o ´invoice_date´ en ese orden.
        """
        self.invoice_date = fields.Date.context_today(self) \
            if not self.invoice_date and not self.date else self.invoice_date or self.date
        self._onchange_invoice_date()
        super(AccountMoveInherited, self).action_post()

    @api.model
    @api.depends('currency_id')
    def _compute_rate_invoice(self):
        for record in self:
            rate_invoice = [r['rate'] for r in record['currency_id']['rate_ids']
                            if record['invoice_date'] == r['name']]
            if rate_invoice:
                record.rate_invoice = rate_invoice[0]
            elif record['company_id']['currency_id']['rate_ids']:
                rate_invoice = [r['rate'] for r in record['company_id']['currency_id']['rate_ids']
                                if record['invoice_date'] == r['name']]
                if rate_invoice:
                    record.rate_invoice = rate_invoice[0]
                else:
                    record.rate_invoice = record['company_id']['currency_id']['rate']
            else:
                record.rate_invoice = record['currency_id']['rate']
    # Necesario para Coversion segun tasa de cambio

    def _set_reference(self):
        for rec in self:
            if rec.invoice_doc_serie:
                rec.invoice_ref = '%s %s-%s' % (
                    rec.invoice_doc_type.name, rec.invoice_doc_serie, rec.invoice_doc_number)

            else:
                rec.invoice_ref = '%s %s' % (rec.invoice_doc_type.name, rec.invoice_doc_number)

    def _get_sequence(self):
        """ Return the sequence to be used during the post of the current move.
        :return: An ir.sequence record or False.
        """
        self.ensure_one()

        journal = self.journal_id
        if self.move_type in (
                'entry', 'out_invoice', 'in_invoice', 'out_receipt', 'in_receipt') or not journal.refund_sequence:
            return journal.sequence_id
        if not journal.refund_sequence_id:
            return
        return journal.refund_sequence_id

    def _post(self, soft=True):
        """Post/Validate the documents.
               Posting the documents will give it a number, and check that the document is
               complete (some fields might not be required if not posted but are required
               otherwise).
               If the journal is locked with a hash table, it will be impossible to change

               some fields afterwards.
               :param soft (bool): if True, future documents are not immediately posted,
                   but are set to be auto posted automatically at the set accounting date.
                   Nothing will be performed on those documents before the accounting date.
               :return Model<account.move>: the documents that have been posted
               """

        if soft:
            future_moves = self.filtered(lambda move: move.date > fields.Date.context_today(self))
            future_moves.auto_post = True
            for move in future_moves:
                msg = _('This move will be posted at the accounting date: %(date)s',
                        date=format_date(self.env, move.date))
                move.message_post(body=msg)
            to_post = self - future_moves
        else:
            to_post = self

        # `user_has_group` won't be bypassed by `sudo()` since it doesn't change the user anymore.
        if not self.env.su and not self.env.user.has_group('account.group_account_invoice'):
            raise AccessError(_("You don't have the access rights to post an invoice."))
        for move in to_post:
            if move.state == 'posted':
                raise UserError(_('The entry %s (id %s) is already posted.') % (move.name, move.id))
            if not move.line_ids.filtered(lambda line: not line.display_type):
                raise UserError(_('You need to add a line before posting.'))
            if move.auto_post and move.date > fields.Date.context_today(self):
                date_msg = move.date.strftime(get_lang(self.env).date_format)
                raise UserError(_("This move is configured to be auto-posted on %s", date_msg))

            if not move.partner_id:
                if move.is_sale_document():
                    raise UserError(
                        _("The field 'Customer' is required, please complete it to validate the Customer Invoice."))
                elif move.is_purchase_document():
                    raise UserError(
                        _("The field 'Vendor' is required, please complete it to validate the Vendor Bill."))

            if move.is_invoice(include_receipts=True) and float_compare(move.amount_total, 0.0,
                                                                        precision_rounding=move.currency_id.rounding) < 0:
                raise UserError(
                    _("You cannot validate an invoice with a negative total amount. You should create a credit note instead. Use the action menu to transform it into a credit note or refund."))

            # Handle case when the invoice_date is not set. In that case, the invoice_date is set at today and then,
            # lines are recomputed accordingly.
            # /!\ 'check_move_validity' must be there since the dynamic lines will be recomputed outside the 'onchange'
            # environment.
            if not move.invoice_date:
                if move.is_sale_document(include_receipts=True):
                    move.invoice_date = fields.Date.context_today(self)
                    move.with_context(check_move_validity=False)._onchange_invoice_date()
                elif move.is_purchase_document(include_receipts=True):
                    raise UserError(_("The Bill/Refund date is required to validate this document."))

            # When the accounting date is prior to the tax lock date, move it automatically to the next available date.
            # /!\ 'check_move_validity' must be there since the dynamic lines will be recomputed outside the 'onchange'
            # environment.
            if (move.company_id.tax_lock_date and move.date <= move.company_id.tax_lock_date) and (
                    move.line_ids.tax_ids or move.line_ids.tax_tag_ids):
                move.date = move._get_accounting_date(move.invoice_date or move.date, True)
                move.with_context(check_move_validity=False)._onchange_currency()

        # Create the analytic lines in batch is faster as it leads to less cache invalidation.
        to_post.mapped('line_ids').create_analytic_lines()
        to_post.write({
            'state': 'posted',
            'posted_before': True,
        })

        for move in to_post:
            move.message_subscribe([p.id for p in [move.partner_id] if p not in move.sudo().message_partner_ids])
            # Get the journal's sequence.
            sequence = move._get_sequence()
            if not sequence:
                raise UserError(_('Please define a sequence on your journal.'))

            # Consume a new number.
            if move.move_type == 'out_invoice' or move.move_type == "out_refund":
                to_write = {'invoice_doc_type': sequence.l10n_latam_document_type_id, 'invoice_doc_serie':
                    sequence._get_prefix_suffix(date=move.invoice_date or fields.Date.today(),
                                                date_range=move.invoice_date)[0],
                            'invoice_doc_number': '%%0%sd' % sequence.padding % sequence._get_current_sequence().number_next_actual,
                            'name': sequence.next_by_id(sequence_date=move.date)}
                move.write(to_write)

            # Compute 'ref' for 'out_invoice'.
            if move._auto_compute_invoice_reference():
                to_write = {
                    'payment_reference': move._get_invoice_computed_reference(),
                    'line_ids': []
                }
                for line in move.line_ids.filtered(
                        lambda line: line.account_id.user_type_id.type in ('receivable', 'payable')):
                    to_write['line_ids'].append((1, line.id, {'name': to_write['payment_reference']}))
                move.write(to_write)

        for move in to_post:
            if move.is_sale_document() \
                    and move.journal_id.sale_activity_type_id \
                    and (move.journal_id.sale_activity_user_id or move.invoice_user_id).id not in (
                    self.env.ref('base.user_root').id, False):
                move.activity_schedule(
                    date_deadline=min((date for date in move.line_ids.mapped('date_maturity') if date),
                                      default=move.date),
                    activity_type_id=move.journal_id.sale_activity_type_id.id,
                    summary=move.journal_id.sale_activity_note,
                    user_id=move.journal_id.sale_activity_user_id.id or move.invoice_user_id.id,
                )

        customer_count, supplier_count = defaultdict(int), defaultdict(int)
        for move in to_post:
            if move.is_sale_document():
                customer_count[move.partner_id] += 1
            elif move.is_purchase_document():
                supplier_count[move.partner_id] += 1
        for partner, count in customer_count.items():
            (partner | partner.commercial_partner_id)._increase_rank('customer_rank', count)
        for partner, count in supplier_count.items():
            (partner | partner.commercial_partner_id)._increase_rank('supplier_rank', count)

        # Trigger action for paid invoices in amount is zero
        to_post.filtered(
            lambda m: m.is_invoice(include_receipts=True) and m.currency_id.is_zero(m.amount_total)
        ).action_invoice_paid()

        # Force balance check since nothing prevents another module to create an incorrect entry.
        # This is performed at the very end to avoid flushing fields before the whole processing.
        to_post._check_balanced()
        return to_post

    @api.constrains('invoice_doc_serie', 'invoice_doc_number')
    def _check_duplicate_supplier_reference(self):
        for invoice in self:
            # refuse to validate a vendor bill/credit note if there already exists one with the same reference for
            # the same partner, because it's probably a double encoding of the same bill/credit note only if the two
            # invoices are validated.
            self.ensure_one()
            if invoice.move_type in (
                    'in_invoice', 'in_refund') and invoice.invoice_doc_number and invoice.invoice_doc_serie:
                res = self.env['account.move'].search([
                    ('move_type', '=', invoice.move_type),
                    ('invoice_doc_serie', '=', invoice.invoice_doc_serie),
                    ('invoice_doc_number', '=', invoice.invoice_doc_number),
                    ('company_id', '=', invoice.company_id.id),
                    ('partner_id', '=', invoice.partner_id.id),
                    ('invoice_doc_type', '=', invoice.invoice_doc_type.id),
                    ('id', '!=', invoice.id),
                    ('state', 'in', ('draft', 'posted'))])
                if res:
                    raise UserError(
                        "Se ha detectado una referencia duplicada para la factura de proveedor. "
                        "Es probable que tengas más de un documento con los mismos datos.")

    def button_cancel(self):
        self.invoice_date = fields.Date.context_today(self) \
            if not self.invoice_date and not self.date else self.invoice_date or self.date
        self._onchange_invoice_date()
        super(AccountMoveInherited, self).button_cancel()

    def action_invoice_draft(self):
        if not self.env.user.has_group('account.group_account_user'):
            raise UserError('No tiene permisos para volver al estado borrador.')
        else:
            super(AccountMoveInherited, self).action_invoice_draft()


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    line_total = fields.Monetary(string='Importe', store=True, readonly=True, compute='_compute_price')
    # Necesario para Coversion segun tasa de cambio
    price_subtotal_signed_2 = fields.Monetary(string="Subtotal segun Tasa de Cambio", readonly=True)

    # Necesario para Coversion segun tasa de cambio

    @api.depends('price_unit', 'discount', 'quantity',
                 'product_id', 'move_id.partner_id', 'move_id.currency_id', 'move_id.company_id',
                 'move_id.invoice_date', 'move_id.date')
    def _compute_price(self):
        for rec in self:
            price = rec.price_unit * (1 - (rec.discount or 0.0) / 100.0)
            rec.line_total = price * rec.quantity
