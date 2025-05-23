###################################################################################
#
#    Copyright (C) 2020 Cetmix OÜ
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

from lxml.html import fromstring, tostring

from odoo import api, fields, models, tools

from ..models.common import BLOCK_QUOTE, DEFAULT_SIGNATURE_LOCATION


########################
# Mail.Compose Message #
########################
class MailComposer(models.TransientModel):
    _inherit = "mail.compose.message"

    def _default_signature_location(self):
        """Set default signature location"""
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "cetmix.message_signature_location",
                DEFAULT_SIGNATURE_LOCATION,
            )
        )

    wizard_mode = fields.Selection(
        selection=[
            ("quote", "Quote Message"),
            ("forward", "Forward Message"),
            ("compose", "Compose New Message"),
        ]
    )
    forward_ref = fields.Reference(
        string="Attach to record",
        selection="_referenceable_models_fwd",
        compute="_compute_forward_ref",
        inverse="_inverse_forward_ref",
    )
    signature_location = fields.Selection(
        [("a", "Message bottom"), ("b", "Before quote"), ("n", "No signature")],
        default=_default_signature_location,
        required=True,
        help="Whether to put signature before or after the quoted text.",
    )

    @api.depends("model", "res_ids")
    def _compute_forward_ref(self):
        """Forward ref is computed only when composing new message.
        Otherwise this field is left empty.
        """
        for rec in self:
            res_ids = rec._evaluate_res_ids()
            if rec.wizard_mode == "compose" and rec.model and res_ids:
                rec.forward_ref = self.env[rec.model].browse(res_ids[0])
            else:
                rec.forward_ref = None

    @api.model
    def _prepare_quoted_body(self, quoted_message, is_quote):
        """Prepare Quoted Body by parent message record

        :param quoted_message: "mail.message" record
        :param is_quote: message is quote
        :return: prepared body with quotation block
        """
        body = BLOCK_QUOTE % {
            "date": tools.misc.format_datetime(self.env, quoted_message.date),
            "author": quoted_message.author_display,
            "subject": quoted_message.subject or "",
            "body": quoted_message.body or "",
        }
        if not is_quote:
            return body
        quote_number = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("cetmix.message_quote_number", 0)
        )
        return self._trim_quote_blocks(body, quote_number)

    @api.model
    def default_get(self, fields_list):
        result = super().default_get(fields_list)
        parent_id = result.get("parent_id")
        wizard_mode = result.get("wizard_mode") or self._context.get(
            "default_wizard_mode"
        )
        if not wizard_mode:
            return result
        if parent_id and wizard_mode in ["quote", "forward"]:
            parent = self.env["mail.message"].browse(parent_id)
            result.update(
                body=self._prepare_quoted_body(parent, wizard_mode == "quote")
            )
        if wizard_mode == "forward":
            result.update(parent_id=False)
        return result

    @api.model
    def _trim_quote_blocks(self, body, limit):
        """Trimming  <blockquote> which exceeding the limit from message body

        :param body: message body
        :param limit: quoted block limit
        :return: cleaned message body
        """
        if limit <= 0:
            return body
        tree = fromstring(body)
        blocks = tree.xpath("//blockquote")
        if not blocks:
            return body
        remove_blocks = blocks[limit:]
        if not remove_blocks:
            return body
        remove_blocks[0].getparent().remove(remove_blocks[0])
        return tostring(tree, encoding="unicode")

    def _inverse_forward_ref(self):
        if self.forward_ref:
            self.update(
                {"model": self.forward_ref._name, "res_ids": self.forward_ref.ids}
            )

    # -- Ref models
    @api.model
    def _referenceable_models_fwd(self):
        return self.env["cx.model.reference"].referenceable_models()

    # -- Send
    def _action_send_mail(self, auto_commit=False):
        return super(
            MailComposer,
            self.with_context(
                signature_location=self.signature_location,
                default_wizard_mode=self.wizard_mode,
            ),
        )._action_send_mail(auto_commit=auto_commit)

    @api.model
    def _prepare_valid_record_partners(self, parent, partner_ids):
        """Prepare partners for record"""
        partner_ids = partner_ids + [
            (4, p.id)
            for p in parent.partner_ids.filtered(
                lambda rec: rec.email
                not in [self.env.user.email, self.env.user.company_id.email]
            )
        ]
        if self._context.get("is_private") and parent.author_id:
            # check message is private then add author also in partner list.
            partner_ids += [(4, parent.author_id.id)]
        return partner_ids

    @api.model
    def _prepare_subject_with_prefix(self, wizard_mode, subject):
        if not subject:
            return subject
        if wizard_mode == "forward":
            prefix, prefix_str = "Fwd:", self.env._("Fwd:")
        elif wizard_mode == "quote":
            prefix, prefix_str = "Re:", self.env._("Re:")
        else:
            return subject
        if not (subject.startswith(prefix) or subject.startswith(prefix_str)):
            return f"{prefix_str} {subject}"
        return subject

    @api.depends(
        "composition_mode",
        "model",
        "parent_id",
        "record_name",
        "res_domain",
        "res_ids",
        "template_id",
    )
    @api.depends_context("default_wizard_mode")
    def _compute_subject(self):
        result = super()._compute_subject()
        wizard_mode = self._context.get("default_wizard_mode")
        for composer in self:
            subject = composer.subject
            if subject and composer.model and composer.composition_mode == "comment":
                composer.subject = self._prepare_subject_with_prefix(
                    wizard_mode, subject
                )
        return result
