# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import api, fields, models


class AccountDocumentReversal(models.AbstractModel):
    _name = "account.document.reversal"
    _description = "Abstract Module for Document Reversal"

    is_cancel_reversal = fields.Boolean(
        string="Use Cancel Reversal", compute="_compute_is_cancel_reversal",
    )

    def _compute_is_cancel_reversal(self):
        """ Based on setting in document's journal """
        for rec in self:
            rec.is_cancel_reversal = (
                rec.journal_id.is_cancel_reversal if "journal_id" in rec else False
            )

    @api.model
    def reverse_document_wizard(self):
        """ Return Wizard to Cancel Document """
        action = self.env.ref(
            "account_document_reversal.action_view_reverse_account_document"
        )
        vals = action.read()[0]
        return vals

    def action_document_reversal(self, date=None, journal_id=None):
        """ Reverse with following guildeline,
        - Check existing document state / raise warning
        - Find all related moves and unreconcile
        - Create reversed moves
        - Set state to cancel
        """
        raise NotImplementedError()

    def cancel_reversal(self):
        return self.reverse_document_wizard()

    def action_draft(self):
        """ Case cancel reversal, set to draft allowed only when no moves """
        for rec in self:
            if rec.is_cancel_reversal and rec.move_line_ids:
                raise UserError(_("Cannot set to draft!"))
        return super().action_draft()

    def cancel(self):
        if any(self.mapped("is_cancel_reversal")):
            raise UserError(_("Please use cancel_reversal()"))
        return super().cancel()

    def action_document_reversal(self, date=None, journal_id=None):
        """ Reverse all moves related to this payment + set state to cancel """
        # Check document readiness
        valid_state = (
            len(self.mapped("state")) == 1
            and list(set(self.mapped("state")))[0] == "posted"
        )
        if not valid_state:
            raise UserError(_("Only validated document can be cancelled (reversal)"))
        # Find moves to get reversed
        move_lines = self.mapped("move_line_ids").filtered(
            lambda x: x.journal_id == self.mapped("journal_id")[0]
        )
        moves = move_lines.mapped("move_id")
        # Create reverse entries
        moves._cancel_reversal(journal_id)
        # Set state cancelled and unlink with account.move
        self.write({"state": "cancelled"})
        return True

    def button_cancel_reconciliation(self):
        """ If cancel method is to reverse, use document reversal wizard """
        cancel_reversal = all(
            self.mapped("journal_entry_ids.move_id.journal_id.is_cancel_reversal")
        )
        states = self.mapped("statement_id.state")
        if cancel_reversal:
            if not all(st == "open" for st in states):
                raise UserError(_("Only new bank statement can be cancelled"))
            return self.reverse_document_wizard()
        return super().button_cancel_reconciliation()

    def action_document_reversal(self, date=None, journal_id=None):
        """ Reverse all moves related to this statement + delete payment """
        # This part is from button_cancel_reconciliation()
        aml_to_unbind = self.env["account.move.line"]
        aml_to_cancel = self.env["account.move.line"]
        payment_to_unreconcile = self.env["account.payment"]
        payment_to_cancel = self.env["account.payment"]
        for st_line in self:
            aml_to_unbind |= st_line.journal_entry_ids
            for line in st_line.journal_entry_ids:
                payment_to_unreconcile |= line.payment_id
                if (
                    st_line.move_name
                    and line.payment_id.payment_reference == st_line.move_name
                ):
                    # there can be several moves linked to a statement line
                    # but maximum one created by the line itself
                    aml_to_cancel |= line
                    payment_to_cancel |= line.payment_id
        aml_to_unbind = aml_to_unbind - aml_to_cancel

        if aml_to_unbind:
            aml_to_unbind.write({"statement_line_id": False})

        payment_to_unreconcile = payment_to_unreconcile - payment_to_cancel
        if payment_to_unreconcile:
            payment_to_unreconcile.unreconcile()
        # --

        # Find account moves to cancel reversal
        moves = aml_to_cancel.mapped("move_id")
        # Create reverse entries
        moves._cancel_reversal(journal_id)
        # Set cancel related payments
        payment_to_cancel.write({"state": "cancelled"})
        return True


    cancel_reversal = fields.Boolean(
        string="Cancel Reversal",
        default=False,
        copy=False,
        help="This document is being cancelled by using reversal method",
    )
    reverse_entry_id = fields.Many2one(
        comodel_name="account.move",
        string="Reversed by",
        compute="_compute_reverse_entry_id",
        help="The move that reverse this move (opposite of reversed_entry_id)",
    )

    def _compute_reverse_entry_id(self):
        res = self.sudo().search_read(
            fields=["id", "reversed_entry_id"],
            domain=[("reversed_entry_id", "in", self.ids)],
        )
        reverse_entries = {x["reversed_entry_id"][0]: x["id"] for x in res}
        for move in self:
            move.reverse_entry_id = reverse_entries.get(move.id, False)

    def button_cancel_reversal(self):
        return self.reverse_document_wizard()

    def button_draft(self):
        for rec in self:
            if rec.is_cancel_reversal and rec.state != "cancel":
                raise UserError(_("Cannot set to draft!"))
        return super().button_draft()

    def button_cancel(self):
        if any(self.mapped("is_cancel_reversal")):
            raise UserError(_("Please use button_cancel_reversal()"))
        return super().button_cancel()

    def action_document_reversal(self, date=None, journal_id=None):
        # Check document readiness
        valid_state = (
            len(self.mapped("state")) == 1
            and list(set(self.mapped("state")))[0] == "posted"
        )
        if not valid_state:
            raise UserError(_("Only posted document can be cancelled (reversal)"))
        if self.mapped("line_ids.matched_debit_ids") | self.mapped(
            "line_ids.matched_credit_ids"
        ):
            raise UserError(
                _(
                    "Only fully unpaid invoice can be cancelled.\n"
                    "To cancel this invoice, make sure all payment(s) "
                    "are also cancelled."
                )
            )
        # Create reverse entries
        self._cancel_reversal(journal_id)
        return True

    def _cancel_reversal(self, journal_id):
        self.mapped("line_ids").filtered(
            lambda x: x.account_id.reconcile
        ).remove_move_reconcile()
        Reversal = self.env["account.move.reversal"]
        res = Reversal.with_context(
            active_ids=self.ids, active_model="account.move"
        ).default_get([])
        res.update(
            {"journal_id": journal_id, "refund_method": "cancel", "move_type": "entry"}
        )
        reversal = Reversal.create(res)
        reversal.with_context(cancel_reversal=True).reverse_moves()

    def _reverse_moves(self, default_values_list=None, cancel=False):
        """ Set flag on the moves and the reversal moves being reversed """
        if self._context.get("cancel_reversal"):
            self.write({"cancel_reversal": True})
        reverse_moves = super()._reverse_moves(default_values_list, cancel)
        if self._context.get("cancel_reversal"):
            reverse_moves.write({"cancel_reversal": True})
        return reverse_moves

    def _reverse_move_vals(self, default_values, cancel=True):
        """ Reverse with cancel reversal, always use move_type = entry """
        if self._context.get("cancel_reversal"):
            default_values.update({"type": "entry"})
        return super()._reverse_move_vals(default_values, cancel)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def remove_move_reconcile(self):
        """ Freeze move with cancel_reversal = True, disallow unreconcile """
        if not self._context.get("cancel_reversal") and any(
            self.mapped("move_id").mapped("cancel_reversal")
        ):
            raise UserError(
                _(
                    "This document was cancelled and freozen,\n"
                    "unreconcilation not allowed."
                )
            )
        return super().remove_move_reconcile()