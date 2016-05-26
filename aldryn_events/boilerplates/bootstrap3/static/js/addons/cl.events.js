/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

var Cl = window.Cl || {};

(function ($) {
    'use strict';
    var MONTHS_IN_YEAR = 12;

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
            var month = parseInt(table.data('month-numeric'), 10);
            var year = parseInt(table.data('year'), 10);
            var title = calendar.find('h3');

            // cancel if no direction is provided
            if (!direction) {
                return false;
            }

            // handle first and last bound
            if (direction === 'next') {
                if (month === MONTHS_IN_YEAR) {
                    month = 1;
                    year += 1;
                } else {
                    month += 1;
                }
            }
            if (direction === 'previous') {
                if (month === 1) {
                    month = MONTHS_IN_YEAR;
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
                    // eslint-disable-next-line
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
