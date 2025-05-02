odoo.define('hibarr_webmail_final.webmail_notification', function (require) {
    "use strict";
    var bus = require('bus.bus_service');
    var Notification = require('web.Notification');
    var core = require('web.core');
    var session = require('web.session');

    bus.addChannel('webmail.new_email');
    bus.on('notification', null, function (notifications) {
        notifications.forEach(function (notification) {
            if (notification[0][1] === 'webmail.new_email') {
                var data = notification[1];
                core.bus.trigger('do_notify', {
                    title: 'New Email from ' + (data.sender || ''),
                    message: (data.subject || '') + '<br>' + (data.body || ''),
                    sticky: false,
                    type: 'info',
                });
            }
        });
    });
});
