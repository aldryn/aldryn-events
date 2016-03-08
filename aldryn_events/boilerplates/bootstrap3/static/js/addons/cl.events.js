/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

//######################################################################################################################
// #NAMESPACES#
var Cl = window.Cl || {};

//######################################################################################################################
// #UTILS#
(function ($) {
    'use strict';

    Cl.events = {

        // INFO: autoinit certain functionalities
        init: function () {
            var that = this;

            $('.js-events-calendar').each(function () {
                that.calendar($(this));
            });
        },

        _handler: function (e) {
            e.preventDefault();
            var calendar = $(this).closest('.events-calendar');
            var settings = calendar.data();
            var direction = $(this).data('direction');
            var table = calendar.find('.table-calendar');
            var month = parseInt(table.data('month-numeric'));
            var year = parseInt(table.data('year'));
            var title = calendar.find('h3');

            // cancel if no direction is provided
            if (!direction) {
                return false;
            }

            // handle first and last bound
            if (direction === 'next') {
                if (month === 12) {
                    month = 1;
                    year += 1;
                } else {
                    month += 1;
                }
            }
            if (direction === 'previous') {
                if (month === 1) {
                    month = 12;
                    year -= 1;
                } else {
                    month -= 1;
                }
            }

            // send proper ajax request
            $.ajax({
                type: 'get',
                url: settings.url + year + '/' + month + '/?plugin_pk=' + settings.pk,
                success: function (data) {
                    table.replaceWith(data);
                    title.html($(data).data('month') + ' ' + $(data).data('year'));
                },
                error: function () {
                    alert(settings.error);
                }
            });
        },

        // INFO: handle calendar
        calendar: function (calendar) {
            // attach events
            calendar.on('click', '.controls .js-trigger', this._handler);
        }

    };

    // autoload
    if ($('.js-events-calendar').length) {
        Cl.events.init();
    }

})(jQuery);
