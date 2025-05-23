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

from odoo.tests import tagged

from .common import MailMessageCommon


@tagged("post_install", "-at_install")
class TestMailMessageBase(MailMessageCommon):
    def setUp(self):
        super().setUp()
        group_user_id = self.env.ref("base.group_user").id
        group_conversation_own_id = self.env.ref(
            "prt_mail_messages.group_conversation_own"
        ).id

        self.test_user = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Test User #2",
                    "login": "test_user2",
                    "email": "test@example.com",
                    "groups_id": [
                        (4, group_user_id),
                        (4, group_conversation_own_id),
                    ],
                }
            )
        )

        self.conversation_A = self.env["cetmix.conversation"].create(
            {
                "active": True,
                "name": "Conversation A",
                "partner_ids": [(4, self.test_user.partner_id.id)],
            }
        )

        self.domain_conversation_A = [
            ("model", "=", "cetmix.conversation"),
            ("res_id", "=", self.conversation_A.id),
            ("message_type", "!=", "notification"),
        ]

        for message_count in range(10):
            self.conversation_A.sudo().message_post(
                body=f"Message - {message_count}",
                message_type="email",
            )

        self.messages_available = (
            self.env["mail.message"]
            .with_user(self.test_user)
            .with_context(check_messages_access=False)
            .search(self.domain_conversation_A)
        )

        self.message_available_count = len(self.messages_available)

    # def test_get_mail_thread_data_res_partner(self):
    #     """Test flow get thread data for `res.partner` record"""
    #     result = self.res_partner_ann._get_mail_thread_data([])
    #     self.assertTrue(result.get("hasWriteAccess"))
    #     self.assertTrue(result.get("hasReadAccess"))
    #     self.assertFalse(result.get("canPostOnReadonly"))
    #
    # def test_get_mail_thread_data_res_users(self):
    #     """Test flow get thread data for `res.users` record"""
    #     result = self.res_users_internal_user_email._get_mail_thread_data([])
    #     self.assertTrue(result.get("hasReadAccess"))
    #     self.assertFalse(result.get("hasWriteAccess"))
    #
    # def test_get_mail_thread_data_empty_user(self):
    #     """Test flow get thread data for `res.users` empty record"""
    #     result = self.env["res.users"]._get_mail_thread_data([])
    #     self.assertFalse(result.get("hasReadAccess"))
    #     self.assertFalse(result.get("hasWriteAccess"))

    def test_create_conversation_message(self):
        conversation = self.env["cetmix.conversation"].create(
            {"name": "Conversation #1"}
        )
        msg_conversation_1 = self.env["mail.message"].create(
            {
                "author_id": self.res_partner_ann.id,
                "body": "Message #1",
                "partner_ids": [
                    (4, self.env.user.partner_id.id),
                    (4, self.res_partner_kate.id),
                    (4, self.res_partner_mark.id),
                ],
                "res_id": conversation.id,
                "model": conversation._name,
            }
        )
        self.assertEqual(
            conversation.last_message_by.id,
            msg_conversation_1.author_id.id,
            msg=f"Last message author ID must be equal to {self.res_partner_ann.id}",
        )
        msg_conversation_2 = self.env["mail.message"].create(
            {
                "author_id": self.res_partner_kate.id,
                "body": "Message #2",
                "partner_ids": [
                    (4, self.res_partner_kate.id),
                ],
                "res_id": conversation.id,
                "model": conversation._name,
            }
        )
        self.assertEqual(
            conversation.last_message_by.id,
            msg_conversation_2.author_id.id,
            msg=f"Last message author ID must be equal to {self.res_partner_kate.id}",
        )

    def test_mail_message_search1(self):
        """Test flow that check correct _search method work"""
        messages = (
            self.env["mail.message"]
            .with_context(check_messages_access=True)
            .with_user(self.test_user.id)
            .search(self.domain_conversation_A, limit=self.message_available_count / 2)
        )
        self.assertEqual(len(messages), 5)
        for message in messages:
            self.assertIn(message.id, self.messages_available.ids)

        last_messages = (
            self.env["mail.message"]
            .with_context(check_messages_access=True, last_id=messages[-1].id)
            .with_user(self.test_user.id)
            .search(
                self.domain_conversation_A,
                limit=self.message_available_count * 2,
                offset=len(messages),
            )
        )
        messages = messages | last_messages
        self.assertEqual(len(self.messages_available), len(messages))
        self.assertListEqual(messages.ids, self.messages_available.ids)

    def test_mail_message_search2(self):
        """Test flow that check correct _search method work without limit"""
        message_ids = (
            self.env["mail.message"]
            .with_context(check_messages_access=True)
            .with_user(self.test_user.id)
            .search(self.domain_conversation_A, limit=False)
        )
        self.assertEqual(len(self.messages_available), len(message_ids))
        self.assertListEqual(message_ids.ids, self.messages_available.ids)

    def test_search_messages(self):
        """Test flow that check correct search message by domain"""
        message_ids = self.messages_available.ids
        messages_struct = self.env["mail.message"]._search_messages(
            [("id", "in", message_ids)]
        )
        messages_dict = [
            {"id": id_, "model": model, "res_id": res_id, "message_type": message_type}
            for id_, model, res_id, message_type in reversed(messages_struct)
        ]
        self.assertRecordValues(self.messages_available, messages_dict)

        messages_struct = self.env["mail.message"]._search_messages(
            [("id", "=", False)]
        )

        self.assertListEqual(messages_struct, [])

        messages_struct = self.env["mail.message"]._search_messages([(0, "=", 1)])
        self.assertListEqual(messages_struct, [])

    def test_prepare_search_domain_last_id(self):
        message_id = self.messages_available[0].id

        search_domain, order, scroll_back = self.env[
            "mail.message"
        ]._prepare_search_domain(
            [],
            message_id,
            False,
            False,
            False,
            False,
        )
        self.assertEqual(search_domain, ("id", "<", message_id))
        self.assertEqual(order, "id desc")
        self.assertFalse(scroll_back)

        search_domain, order, scroll_back = self.env[
            "mail.message"
        ]._prepare_search_domain(
            [],
            message_id,
            False,
            False,
            False,
            True,
        )
        self.assertEqual(search_domain, ("id", ">", message_id))
        self.assertEqual(order, "id asc")
        self.assertTrue(scroll_back)

    def test_prepare_search_domain_offset(self):
        search_domain, order, scroll_back = self.env[
            "mail.message"
        ]._prepare_search_domain(
            [],
            False,
            False,
            False,
            "id desc",
            True,
        )
        self.assertFalse(search_domain)
        self.assertEqual(order, "id desc")
        self.assertTrue(scroll_back)

    def test_prepare_search_domain_last_offset(self):
        message_id = self.messages_available[0].id

        search_domain, order, scroll_back = (
            self.env["mail.message"]
            .with_context(last_offset=10, first_id=message_id)
            ._prepare_search_domain(
                [],
                False,
                False,
                5,
                "id desc",
                True,
            )
        )
        self.assertEqual(search_domain, ("id", ">", message_id))
        self.assertEqual(order, "id asc")
        self.assertTrue(scroll_back)

        search_domain, order, scroll_back = (
            self.env["mail.message"]
            .with_context(last_offset=0, first_id=message_id)
            ._prepare_search_domain(
                [],
                False,
                3,
                5,
                "id desc",
                True,
            )
        )
        self.assertFalse(search_domain)
        self.assertEqual(order, "id asc")
        self.assertTrue(scroll_back)
        search_domain, order, scroll_back = (
            self.env["mail.message"]
            .with_context(last_offset=3, last_id=message_id)
            ._prepare_search_domain(
                [],
                False,
                5,
                5,
                "id desc",
                True,
            )
        )
        self.assertEqual(search_domain, ("id", "<", message_id))
        self.assertEqual(order, "id desc")
        self.assertTrue(scroll_back)
        search_domain, order, scroll_back = (
            self.env["mail.message"]
            .with_context(last_offset=3, first_id=message_id)
            ._prepare_search_domain(
                [],
                False,
                5,
                3,
                "id desc",
                True,
            )
        )
        self.assertEqual(search_domain, ("id", "<=", message_id))
        self.assertEqual(order, "id desc")
        self.assertTrue(scroll_back)

    def test_mail_message_remove_messages_at_unlink_source_record(self):
        """Test flow that check unlink messages at unlink source record"""
        conversation = self.env["cetmix.conversation"].create(
            {"name": "Conversation Test"}
        )
        conversation_messages = self.env["mail.message"].create(
            [
                {
                    "author_id": self.res_partner_ann.id,
                    "body": "Conversation Message #1",
                    "partner_ids": [(4, self.env.user.partner_id.id)],
                    "res_id": conversation.id,
                    "model": conversation._name,
                },
                {
                    "author_id": self.res_partner_ann.id,
                    "body": "Conversation Message #2",
                    "partner_ids": [(4, self.env.user.partner_id.id)],
                    "res_id": conversation.id,
                    "model": conversation._name,
                },
            ]
        )
        message_ids = conversation_messages.ids
        message1 = conversation_messages[0]
        message1.unlink_pro()
        # Verify message is in trash/archived
        archived_message = (
            self.env["mail.message"].with_context(active_test=False).browse(message1.id)
        )
        self.assertTrue(
            archived_message.exists(), "Message should exist in archived state"
        )
        self.assertFalse(archived_message.active, "Message should be archived")
        conversation.unlink()
        messages = (
            self.env["mail.message"]
            .with_context(active_test=True)
            .search([("id", "in", message_ids)])
        )
        self.assertFalse(messages)
