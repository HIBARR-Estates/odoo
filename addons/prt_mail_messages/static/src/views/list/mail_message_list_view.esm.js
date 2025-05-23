import {ConversationUpdateListRenderer} from "./conversation_list_renderer.esm";
import {MailMessageUpdateListController} from "./mail_message_list_controller.esm";
import {MailMessageUpdateListModel} from "./mail_message_list_model.esm";
import {MailMessageUpdateListRenderer} from "./mail_message_list_renderer.esm";
import {listView} from "@web/views/list/list_view";
import {registry} from "@web/core/registry";

export const mailMessageListView = {
    ...listView,
    Controller: MailMessageUpdateListController,
    Renderer: MailMessageUpdateListRenderer,
    Model: MailMessageUpdateListModel,
};

export const mailConversationListView = {
    ...listView,
    Renderer: ConversationUpdateListRenderer,
};

registry.category("views").add("prt_mail_message_list", mailMessageListView);
registry.category("views").add("mail_conversation_list", mailConversationListView);
