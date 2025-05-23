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

import logging
import re
import textwrap
from collections import defaultdict
from datetime import timedelta
from email.utils import parseaddr

from odoo import api, fields, models
from odoo.exceptions import AccessError
from odoo.osv import expression
from odoo.tools import SQL
from odoo.tools.mail import html_to_inner_content

from .tools import _prepare_date_display  # , _prepare_notification_icon

_logger = logging.getLogger(__name__)

# List of forbidden models
FORBIDDEN_MODELS = ["discuss.channel", "mail.message"]

# Search for 'ghost' models is performed
GHOSTS_CHECKED = False


################
# Mail.Message #
################
class MailMessage(models.Model):
    _inherit = "mail.message"

    author_display = fields.Char(
        string="Message Author", compute="_compute_author_display"
    )

    # Fields to avoid access check issues
    author_allowed_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_author_allowed_id",
        search="_search_author_allowed_id",
    )
    record_ref = fields.Reference(
        string="Message Record",
        selection="_referenceable_models",
        compute="_compute_record_ref",
    )
    thread_messages_count = fields.Integer(
        string="Messages in thread",
        compute="_compute_thread_messages_count",
        help="Total number of messages in thread",
    )
    ref_partner_ids = fields.Many2many(
        string="Followers",
        comodel_name="res.partner",
        compute="_compute_ref_partner_ids",
    )
    model_name = fields.Char(string="Model", compute="_compute_model_name")
    shared_inbox = fields.Boolean(
        compute="_compute_dummy",
        help="Used for Shared Inbox filter only",
        search="_search_shared_inbox",
    )
    cx_edit_uid = fields.Many2one(string="Edited by", comodel_name="res.users")
    cx_edit_date = fields.Datetime(string="Edited on")
    cx_edit_message = fields.Char(
        string="Modified by", compute="_compute_cx_edit_message"
    )

    active = fields.Boolean(default=True)
    delete_uid = fields.Many2one("res.users", string="Deleted by")
    delete_date = fields.Datetime(string="Deleted on")
    deleted_days = fields.Integer(compute="_compute_deleted_days")

    # ---------------- #
    # BEGIN OLD FIELDS #
    # ---------------- #
    partner_count = fields.Integer(
        string="Recipients count", compute="_compute_partner_count"
    )
    attachment_count = fields.Integer(
        string="Attachments count", compute="_compute_attachment_count"
    )
    ref_partner_count = fields.Integer(compute="_compute_ref_partner_count")
    is_note = fields.Boolean(compute="_compute_is_note")

    message_date = fields.Char(compute="_compute_message_date")
    message_date_display = fields.Char(compute="_compute_message_date")

    def _compute_message_date(self):
        for rec in self:
            message_date, date_display = _prepare_date_display(rec, rec.date)
            rec.message_date = (
                message_date and message_date.replace(tzinfo=None) or False
            )
            rec.message_date_display = date_display

    def _compute_is_note(self):
        mt_note = self.env.ref("mail.mt_note").id
        for rec in self:
            rec.is_note = rec.subtype_id.id == mt_note

    @api.depends("partner_ids")
    def _compute_partner_count(self):
        """Count recipients"""
        for rec in self:
            rec.partner_count = len(rec.partner_ids)

    @api.depends("attachment_ids")
    def _compute_attachment_count(self):
        """Count attachments"""
        for rec in self.sudo():
            rec.attachment_count = len(rec.attachment_ids)

    def _compute_ref_partner_count(self):
        """Count ref Partners"""
        for rec in self:
            rec.ref_partner_count = len(rec.ref_partner_ids)

    # ---------------- #
    # END OLD FIELDS #
    # ---------------- #

    # -- Compute count deleted days for message
    def _compute_deleted_days(self):
        """Compute count deleted days for message"""
        now = fields.Datetime.now()
        for rec in self:
            rec.deleted_days = rec.delete_date and (now - rec.delete_date).days or False

    # -- Compute text shown as last edit message
    @api.depends("cx_edit_uid")
    def _compute_cx_edit_message(self):
        # Get current timezone
        # Check messages
        for rec in self:
            if not rec.cx_edit_uid:
                rec.cx_edit_message = False
                continue
            message_date_, date_display = _prepare_date_display(rec, rec.cx_edit_date)
            rec.cx_edit_message = self.env._("Edited by %(name)s %(date)s") % {
                "name": rec.cx_edit_uid.name,
                "date": date_display,
            }

    # -- Search private inbox
    def _search_shared_inbox(self, operator, operand):
        if operator == "=" and operand:
            return [
                "|",
                ("author_id", "=", False),
                ("author_id", "!=", self.env.user.partner_id.id),
            ]
        return [("author_id", "!=", False)]

    # -- Get model name for Form View
    def _compute_model_name(self):
        IrModelSudo = self.env["ir.model"].sudo()
        model_ids = list(set(self.mapped("model")))
        model_dict = {
            model.model: model.name
            for model in IrModelSudo.search([("model", "in", model_ids)])
        }
        for rec in self:
            rec.model_name = (
                model_dict[rec.model] if rec.model else self.env._("Lost Message")
            )

    # -- Star several messages
    def mark_read_multi(self):
        for rec in self:
            if rec.needaction:
                rec.set_message_done()
            if rec.parent_id and rec.parent_id.needaction:
                rec.parent_id.set_message_done()

    # -- Star several messages
    def star_multi(self):
        for rec in self:
            rec.toggle_message_starred()

    # -- Archive/unarchive message
    def archive(self):
        for rec in self.filtered(lambda msg: not msg.delete_date):
            rec.active = not rec.active

    def undelete(self):
        """Undelete message from trash"""
        # Store Conversation ids
        conversations = self.sudo().filtered(lambda r: r.model == "cetmix.conversation")
        if conversations:
            self.env["cetmix.conversation"].search(
                [
                    ("active", "=", False),
                    ("id", "in", conversations.mapped("res_id")),
                ]
            ).with_context(only_conversation=True).write({"active": True})
        self.with_context(undelete_action=True).write(
            {"active": True, "delete_uid": False, "delete_date": False}
        )

    @api.model
    def _unlink_trash_message(self, test_custom_datetime=None):
        """
        Delete old messages by cron
        :param test_custom_datetime - argument for testing
        :return True always
        """
        messages_easy_empty_trash = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("cetmix.messages_easy_empty_trash", 0)
        )
        if messages_easy_empty_trash > 0:
            compute_datetime = fields.Datetime.now() - timedelta(
                days=messages_easy_empty_trash
            )
            result = self.sudo().search(
                [
                    ("active", "=", False),
                    ("delete_uid", "!=", False),
                    ("delete_date", "<=", test_custom_datetime or compute_datetime),
                    ("message_type", "!=", "notification"),
                ]
            )
            result.unlink_pro()
        return True

    # -- Create
    @api.model_create_multi
    def create(self, vals_list):
        if self._name != "mail.message":
            return super().create(vals_list)
        # Update last message date if posting to Conversation
        conversation_dict = dict()
        for vals in vals_list:
            if (
                vals.get("model") == "cetmix.conversation"
                and vals.get("message_type") != "notification"
                and vals.get("author_id")
            ):
                conversation_dict[vals.get("res_id")] = vals.get("author_id")
        messages = super().create(vals_list)
        conversation_obj = self.env["cetmix.conversation"]
        write_date = fields.Datetime.now()
        for conversation_id, author_id in conversation_dict.items():
            conversation_obj.browse(conversation_id).write(
                {
                    "last_message_post": write_date,
                    "last_message_by": author_id,
                }
            )
        return messages

    # -- Delete empty Conversations
    def _get_conversation_messages_to_delete_and_archive(self, conversation_ids):
        conversations_2_archive = []
        conversations_2_delete = []
        for conversation in set(conversation_ids):
            message_all = self.with_context(active_test=False).search(
                [
                    ("res_id", "=", conversation),
                    ("model", "=", "cetmix.conversation"),
                    ("message_type", "!=", "notification"),
                ]
            )
            message_active = message_all.filtered(lambda msg: msg.active)

            if not message_all:
                conversations_2_delete.append(conversation)
            elif not message_active:
                conversations_2_archive.append(conversation)
        return conversations_2_archive, conversations_2_delete

    def _action_conversation_record(self, conversation_ids, action):
        """
        Get action for conversations
        :param conversation_ids: List of Conversation ids
        """
        conversations = (
            self.with_context(active_test=False)
            .env["cetmix.conversation"]
            .search([("id", "in", conversation_ids)])
        )
        return getattr(conversations, action)

    # -- Delete empty Conversations
    def _delete_conversations(self, conversation_ids):
        """
        Deletes all conversations with no messages left.
         Notifications are not considered!
        :param set conversation_ids: List of Conversation ids
        :return: just Return))
        """
        if not conversation_ids:
            return
        # Delete empty Conversations
        (
            conversations_2_archive,
            conversations_2_delete,
        ) = self._get_conversation_messages_to_delete_and_archive(conversation_ids)
        # Delete conversations with no messages
        self._action_conversation_record(conversations_2_delete, "unlink")()
        # Archive conversations
        self._action_conversation_record(conversations_2_archive, "write")(
            {"active": False}
        )

    # -- Check delete rights
    def unlink_rights_check(self):
        """
        Check if user has access right to delete messages
        Raises Access Error or returns True
        :return: True
        """
        # Root
        if self.env.is_superuser():
            return True

        # Can delete messages?
        if not self.env.user.has_group("prt_mail_messages.group_delete"):
            raise AccessError(self.env._("You cannot delete messages!"))

        # Can delete any message?
        if self.env.user.has_group("prt_mail_messages.group_delete_any"):
            return True

        # Check access rights
        error_message = self.env._(
            "You cannot delete the following message"
            "\n Subject: %(subject)s \n\n"
            " Reason: %(reason)s"
        )
        partner_id = self.env.user.partner_id.id
        for rec in self:
            # Can delete if user:
            # - Is Message Author for 'comment' message
            # - Is the only 'recipient' for 'email' message
            # Sent or Is Author?
            if (
                rec.message_type in ["comment", "email_outgoing"]
                and not rec.author_allowed_id.id == partner_id
            ):
                raise AccessError(
                    error_message
                    % {
                        "subject": rec.subject,
                        "reason": self.env._("You are not the message author"),
                    }
                )

            # Received
            if rec.message_type == "email":
                # No recipients
                if not rec.partner_ids:
                    raise AccessError(
                        error_message
                        % {
                            "subject": rec.subject,
                            "reason": self.env._("Message recipients undefined"),
                        }
                    )

                # Has several recipients?
                if len(rec.partner_ids) > 1:
                    raise AccessError(
                        error_message
                        % {
                            "subject": rec.subject,
                            "reason": self.env._("Message has multiple recipients"),
                        }
                    )

                # Partner is not that one recipient
                if not rec.partner_ids[0].id == partner_id:
                    raise AccessError(
                        error_message
                        % {
                            "subject": rec.subject,
                            "reason": self.env._("You are not the message recipient"),
                        }
                    )

    def _messages_move_to_trash(self):
        """
        Move to trash messages from self
        :return: None
        """
        if not self:
            return
        self.mark_read_multi()
        self.write(
            {
                "active": False,
                "delete_uid": self.env.user.id,
                "delete_date": fields.Datetime.now(),
            }
        )

    def _delete_trashed_messages(self):
        """
        Delete trash message
        :return: None
        """
        if self:
            count = len(self)
            self.unlink()
            _logger.info(
                f"{count} message{'s'[:count ^ 1]} deleted from trash"
                if count > 0
                else "No messages to delete"
            )

    # -- Unlink
    def unlink_pro(self):
        # Store Conversation ids
        conversation_ids = (
            self.sudo()
            .filtered(lambda r: r.model == "cetmix.conversation")
            .mapped("res_id")
        )
        # Check access rights
        self.unlink_rights_check()

        # Delete message
        messages_to_delete = self.filtered(
            lambda msg: not msg.active and msg.delete_uid and msg.delete_date
        )
        messages_to_delete._delete_trashed_messages()

        # Move to trash message
        self.filtered(
            lambda msg: msg.id not in messages_to_delete.ids
        )._messages_move_to_trash()

        self._delete_conversations(conversation_ids)

    # Sometimes user has access to record but does not have access
    #  to author or recipients.
    # Below is a workaround for author, recipient and followers

    # -- Get allowed author
    @api.depends("author_id")
    def _compute_author_allowed_id(self):
        author_ids = self.mapped("author_id").ids
        author_allowed_ids = (
            self.env["res.partner"].search([("id", "in", author_ids)]).ids
        )
        for rec in self:
            author_id = rec.sudo().author_id.id
            rec.author_allowed_id = (
                author_id if author_id in author_allowed_ids else False
            )

    # -- Search allowed authors
    @api.model
    def _search_author_allowed_id(self, operator, value):
        return [("author_id", operator, value)]

    # -- Get related record followers
    # Check if model has 'followers' field
    # and user has access to followers
    @api.depends("record_ref")
    def _compute_ref_partner_ids(self):
        rec_vals = {}
        # Compose dict of {model: [res_ids]}
        # Will be used to check access rights to followers
        for rec in self:
            rec_model = rec.model
            rec_res_id = rec.res_id
            model_vals = rec_vals.get(rec_model, False)
            if not model_vals:
                rec_vals.update({rec_model: [rec_res_id]})
            elif rec.res_id not in model_vals:
                model_vals.append(rec_res_id)
                rec_vals.update({rec_model: model_vals})

        # Get followers for each "model:records"
        follower_ids = set()
        for model, ids in rec_vals.items():
            if not model or not (
                self.pool and issubclass(self.pool[model], self.pool["mail.thread"])
            ):
                continue
            follower_ids.update(
                self.env[model]
                .sudo()
                .search([("id", "in", ids)])
                .mapped("message_partner_ids")
                .ids
            )

        # Filter only partners we have access to
        follower_allowed_ids = self.env["res.partner"].search(
            [("id", "in", list(follower_ids))]
        )

        for rec in self:
            if (
                rec.record_ref
                and self.pool
                and issubclass(self.pool[rec.model], self.pool["mail.thread"])
            ):
                msg_partner_ids = rec.record_ref.sudo().message_partner_ids
                rec.ref_partner_ids = msg_partner_ids.filtered(
                    lambda p: p in follower_allowed_ids
                )
            else:
                rec.ref_partner_ids = False

    @api.depends("body")
    def _compute_preview(self):
        max_preview = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "cetmix.messages_easy_text_preview",
                190,
            )
        )
        for message in self:
            plaintext_ct = html_to_inner_content(message.body)
            # Customise message review by config parameter
            message.preview = textwrap.shorten(plaintext_ct, max_preview)

    # -- Dummy
    def _compute_dummy(self):
        return

    def _display_number_days_after_deletion(self):
        """Get string of display number days after deletion"""
        if self.delete_date:
            return (
                "Deleted less than one day ago"
                if self.deleted_days == 0
                else f"Deleted {self.deleted_days} days ago"
            )

    @api.model
    def get_message_note_color(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("cetmix.messages_easy_color_note", default=False)
        )

    # -- Get Author for list view
    @api.depends("author_allowed_id")
    def _compute_author_display(self):
        """Get Author for list view"""
        for rec in self:
            rec.author_display = (
                rec.author_allowed_id.name
                if rec.author_allowed_id
                else re.sub(r"[>|<]", "", rec.email_from or "")
            )

    # -- Count messages in same thread
    @api.depends("res_id")
    def _compute_thread_messages_count(self):
        """Count messages in same thread"""
        for rec in self:
            rec.thread_messages_count = self.search_count(
                [
                    "&",
                    "&",
                    ("model", "=", rec.model),
                    ("res_id", "=", rec.res_id),
                    ("message_type", "in", ["email", "comment", "email_outgoing"]),
                ]
            )

    # -- Ref models
    @api.model
    def _referenceable_models(self):
        """List referencable Ref models"""
        ir_model_obj = self.env["ir.model"].sudo()
        return [
            (x.model, x.name) for x in ir_model_obj.search([("transient", "=", False)])
        ]

    # -- Compose reference
    @api.depends("res_id")
    def _compute_record_ref(self):
        for rec in self:
            if rec.model and rec.res_id:
                res = self.env[rec.model].browse(rec.res_id)
                result = res.has_access("read")
                if result:
                    rec.record_ref = res
                    continue
            rec.record_ref = False

    # -- Open messages of the same thread
    def thread_messages(self):
        self.ensure_one()

        list_view_id = self.env.ref("prt_mail_messages.prt_mail_message_list").id
        form_view_id = self.env.ref("prt_mail_messages.prt_mail_message_form").id

        return {
            "name": self.env._("Messages"),
            "views": [[list_view_id, "list"], [form_view_id, "form"]],
            "res_model": "mail.message",
            "type": "ir.actions.act_window",
            "target": "current",
            "domain": [
                ("message_type", "in", ["email", "comment", "email_outgoing"]),
                ("model", "=", self.model),
                ("res_id", "=", self.res_id),
            ],
        }

    # -- Get forbidden models
    def _get_forbidden_models(self):
        # Ghosts checked?
        global GHOSTS_CHECKED
        global FORBIDDEN_MODELS

        if GHOSTS_CHECKED:
            return FORBIDDEN_MODELS[:]

        # Add transient models
        FORBIDDEN_MODELS += (
            self.env["ir.model"]
            .sudo()
            .search([("transient", "=", True)])
            .mapped("model")
        )

        # Search for 'ghost' models. These are models left from uninstalled modules.
        self._cr.execute(
            """ SELECT model FROM ir_model
                                    WHERE transient = False
                                    AND NOT model = ANY(%s) """,
            (list(FORBIDDEN_MODELS),),
        )

        # Check each model
        for msg_model in self._cr.fetchall():
            model = msg_model[0]
            if not self.env["ir.model"].sudo()._get(model).modules:
                FORBIDDEN_MODELS.append(model)

        # Mark as checked
        GHOSTS_CHECKED = True
        return FORBIDDEN_MODELS[:]

    # -- Return allowed message ids and forbidden model list
    @api.model
    def _find_allowed_doc_ids_plus(self, model_ids):
        IrModelAccess = self.env["ir.model.access"]
        allowed_ids, failed_models = set(), set()
        for doc_model, doc_dict in model_ids.items():
            if not IrModelAccess.check(doc_model, "read", False):
                failed_models.add(doc_model)
                continue
            allowed_ids |= self._find_allowed_model_wise(doc_model, doc_dict)
        return allowed_ids, list(failed_models)

    # -- Search messages
    def _search_messages(self, domain, limit=None, order=None):
        """
        This a shortcut function for mail.message model only
        """
        if expression.is_false(self, domain):
            # optimization: no need to query, as no record satisfies the domain
            return []

        # make the search query with the default rules
        query = super()._search(domain, limit=limit, order=order)
        self.env.cr.execute(
            query.select(
                SQL.identifier(self._table, "id"),
                SQL.identifier(self._table, "model"),
                SQL.identifier(self._table, "res_id"),
                SQL.identifier(self._table, "message_type"),
            )
        )
        return self._cr.fetchall()

    def _prepare_search_domain(
        self, domain, last_id, limit, offset, order, scroll_back
    ):
        """
        Check which records are we trying to fetch
        For initial query only
        :param domain: search domain
        :param last_id: last message id
        :param limit: limit records in query
        :param offset: count skip records
        :param order: order SQL
        :param scroll_back: scrolling message list pages back (arrow left)
        :return: search_domain, order, scroll_back
        """
        if last_id:
            # Post fetching records
            if scroll_back:
                return ("id", ">", last_id), "id asc", scroll_back
            return ("id", "<", last_id), "id desc", scroll_back

        # If fetching not the first page or performing search_count
        if not offset:
            return domain, order, scroll_back

        last_offset = self._context.get("last_offset", 0)

        if offset < last_offset:
            # Scrolling back
            return ("id", ">", self._context["first_id"]), "id asc", True
        elif last_offset == 0 and offset / limit > 1:
            # Scrolling reverse from first to last page
            return domain, "id asc", True
        elif offset > last_offset:
            # Scrolling forward
            if self._context.get("last_id"):
                return ("id", "<", self._context["last_id"]), "id desc", scroll_back
            else:
                return (
                    (
                        "id",
                        "<=",
                        self._context["last_back_id"],
                    ),
                    "id desc",
                    scroll_back,
                )

        # Returning from form view
        return ("id", "<=", self._context["first_id"]), "id desc", scroll_back

    def _compose_message_search_domain(self, domain, search_domain, forbidden_models):
        """
        Check for forbidden models and compose final domain
        :param domain: search domain base
        :param search_domain: search domain for messages
        :param forbidden_models: list of forbidden models
        :return: domain
        """
        if search_domain and len(forbidden_models) > 0:
            model_domain = expression.AND(
                [[("model", "not in", forbidden_models)], [search_domain]]
            )
            query_args = expression.AND([model_domain, list(domain)])
        elif search_domain:
            query_args = expression.AND([[search_domain], list(domain)])
        elif len(forbidden_models) > 0:
            query_args = expression.AND(
                [[("model", "not in", forbidden_models)], list(domain)]
            )
        else:
            query_args = domain
        return query_args

    def _check_model_access(self, messages):
        """
        Check model access for messages
        :param messages: list of tuples [(id, model, record_id, message_type)]
        :return: allowed message ids, failed access models
        """
        model_ids = defaultdict(lambda: defaultdict(set))
        for id_, model, res_id, message_type in messages:
            if (
                res_id
                and model
                and message_type in ["email", "comment", "email_outgoing"]
            ):
                model_ids[model][res_id].add(id_)
        allowed_ids, failed_models = self._find_allowed_doc_ids_plus(model_ids)
        return allowed_ids, failed_models

    # -- Override _search
    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        """Mail.message overrides generic '_search' defined in 'model' to
         implement own logic for message access rights.
        However sometimes this does not work for us because
         we would like to show only messages posted to the records
        user actually has access to
        Following key in context is used:
        - 'check_messages_access': if not set legacy 'search' is performed
        For the moment we do not show messages posted to discuss.channel
         Model (Discussion Channels)
        Finally we check the following:
        After having received ids of a classic search, keep only:
        - uid has access to related record
        - otherwise: remove the id
        """
        # Skip if not using our own _search
        # Rules do not apply to administrator
        if (
            not self._context.get("check_messages_access", False)
            or self.env.is_superuser()
        ):
            return super()._search(domain, offset, limit, order)

        # Non-employee see only messages with a subtype (aka, no internal logs)
        if not self.env.user._is_internal():
            domain = self._get_search_domain_share() + domain

        forbidden_models = self._get_forbidden_models()  # Get forbidden models
        limit_remaining = limit  # Remaining amount of records we need to fetch
        ids = []  # List of filtered ids we return
        # id of the last message fetched
        # (in case we need to perform more fetches to fill the limit)
        last_id = False
        scroll_back = False  # Scrolling message list pages back (arrow left)
        search_domain = False

        # Fetch messages
        while limit_remaining if limit else True:
            search_domain, order, scroll_back = self._prepare_search_domain(
                search_domain, last_id, limit, offset, order, scroll_back
            )
            query_domain = self._compose_message_search_domain(
                domain, search_domain, forbidden_models
            )
            # Get messages (id, model, res_id)
            result = self._search_messages(query_domain, limit=limit, order=order)
            if len(result) == 0:
                # All done, no more messages left
                break
            # Check model access
            allowed_ids, failed_models = self._check_model_access(result)
            # Append to list of allowed ids,
            # re-construct a list based on ids,
            # because set did not keep the original order
            sorted_ids = []
            messages_added_count = 0
            # Keep adding message ids until we have all remaining messages added
            for msg_id, *__ in result:
                if limit and messages_added_count == limit_remaining:
                    break
                if msg_id in allowed_ids and msg_id not in ids:
                    sorted_ids.append(msg_id)
                    messages_added_count += 1
            if len(sorted_ids) > 0:
                ids += sorted_ids

            if not limit:
                # Break if search was initially limitless
                break
            if len(failed_models) > 0:
                # Add failed models to forbidden models
                forbidden_models += failed_models
            last_id = result[-1][0]  # Set last id

            if limit_remaining:
                limit_remaining -= len(sorted_ids)  # Deduct remaining amount
        id_list = reversed(ids) if scroll_back else ids
        records = self.browse(id_list)
        return records._as_query(order)

    # -- Prepare context for reply or quote message
    def reply_prep_context(self):
        self.ensure_one()
        wizard_mode = self._context.get("wizard_mode", False)
        is_forward = wizard_mode == "forward"
        subtype_id = self.env["ir.model.data"]._xmlid_to_res_id("mail.mt_comment")
        return {
            "default_res_ids": [self.res_id],
            "default_parent_id": self.id,
            "default_model": self.model,
            "default_partner_ids": self.author_allowed_id.ids,
            "default_attachment_ids": is_forward and self.attachment_ids.ids or [],
            "subtype_id": subtype_id,
            "default_wizard_mode": wizard_mode,
        }

    # -- Reply or quote message
    def reply(self):
        self.ensure_one()
        # Mark as read
        self.mark_read_multi()

        return {
            "name": self.env._("New message"),
            "views": [[False, "form"]],
            "res_model": "mail.compose.message",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": self.reply_prep_context(),
        }

    # -- Move message
    def move(self):
        self.ensure_one()
        # Mark as read
        self.mark_read_multi()

        return {
            "name": self.env._("Move messages"),
            "views": [[False, "form"]],
            "res_model": "prt.message.move.wiz",
            "type": "ir.actions.act_window",
            "target": "new",
        }

    # -- Assign author
    def assign_author(self):
        # Mark as read
        self.mark_read_multi()
        name, email = parseaddr(self.email_from)
        return {
            "name": self.env._("Assign Author"),
            "views": [[False, "form"]],
            "res_model": "cx.message.partner.assign.wiz",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {"default_name": name, "default_email": email},
        }

    # -- Edit message
    def message_edit(self):
        self.ensure_one()
        # Mark as read
        self.mark_read_multi()
        return {
            "name": self.env._("Edit"),
            "views": [[False, "form"]],
            "res_model": "cx.message.edit.wiz",
            "type": "ir.actions.act_window",
            "target": "new",
        }

    def write(self, vals):
        if vals.get("active") and not self._context.get("undelete_action"):
            new_self = self.filtered(lambda r: not r.delete_uid and not r.delete_date)
            return super(MailMessage, new_self).write(vals)
        return super().write(vals)

    def _can_edit_by_group(self, all_, own):
        """
        Check access to edit message record
        :param str all_: group name for edit all records
        :param str own: group name for edit own records
        :return bool: Returns a true if user can access to edit the record else a false.
        """
        author_id = self.author_id.id
        partner_id = self.env.user.partner_id.id
        has_group = self.env.user.has_group
        return has_group(all_) or (has_group(own) and author_id == partner_id)

    def _message_can_edit(self):
        if not self or not self.author_id:
            return False
        # Superuser can edit everything:
        if self.env.is_superuser():
            return True
        # Check access rule
        try:
            self.check_access("write")
        except AccessError:
            return False
        subtype = self.subtype_id
        # Note
        if subtype == self.env.ref("mail.mt_note"):
            return self._can_edit_by_group(
                "prt_mail_messages.group_notes_edit_all",
                "prt_mail_messages.group_notes_edit_own",
            )
        # Message
        if subtype == self.env.ref("mail.mt_comment") or not subtype:
            return self._can_edit_by_group(
                "prt_mail_messages.group_messages_edit_all",
                "prt_mail_messages.group_messages_edit_own",
            )
        # Other types are not editable
        return False
