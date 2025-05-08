odoo.define('hibarr_webmail_final.notification', function (require) {
    'use strict';
    var WebClient = require('web.WebClient');
    WebClient.include({
        start: function () {
            this._super.apply(this, arguments);
            this.call('bus_service', 'onNotification', this, this._onNotification);
        },
        _onNotification: function (notifications) {
            var self = this;
            notifications.forEach(function (notification) {
                if (notification[0] === 'webmail.new_email') {
                    self.displayNotification({
                        title: 'New Email',
                        message: notification[1].subject,
                        type: 'info',
                    });
                }
            });
        },
    });
});