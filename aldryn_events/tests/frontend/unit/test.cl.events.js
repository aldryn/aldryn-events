/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

'use strict';
/* global Cl, describe, it, expect, beforeEach, afterEach, fixture, spyOn */

// #############################################################################
// UNIT TEST
describe('cl.events.js:', function () {
    beforeEach(function () {
        fixture.setBase('frontend/fixtures');
        this.markup = fixture.load('calendar.html');
        this.preventEvent = { preventDefault: function () {} };
    });

    afterEach(function () {
        fixture.cleanup();
    });

    it('has available Cl namespace', function () {
        expect(Cl).toBeDefined();
    });

    it('has a public method calendar', function () {
        expect(Cl.events.calendar).toBeDefined();
    });

    describe('Cl.events.init(): ', function () {
        it('returns undefined', function () {
            expect(Cl.events.init()).toEqual(undefined);
        });

        it('runs calendar()', function () {
            spyOn(Cl.events, 'calendar');
            Cl.events.init();

            // validate that calendar was called inside Cl.events.init()
            expect(Cl.events.calendar).toHaveBeenCalled();
            // validate 6 calls as 6 calendars are specified in calendar.html
            expect(Cl.events.calendar.calls.count()).toEqual(6);
        });
    });

    describe('Cl.events._handler: ', function () {
        it('returns false if direction is not specified', function () {
            expect(Cl.events._handler.call(
                $('.js-trigger')[0], this.preventEvent))
                    .toEqual(false);
        });

        it('returns undefined if direction is specified', function () {
            // validate the return of undefined if direction is "next"
            expect(Cl.events._handler.call(
                $('.js-trigger')[1], this.preventEvent))
                    .toEqual(undefined);
            // validate the return of undefined if direction is "previous"
            expect(Cl.events._handler.call(
                $('.js-trigger')[3], this.preventEvent))
                    .toEqual(undefined);
        });

        it('has correct ajax request if direction is "next" and year is ' +
            '2015, month is 7', function () {
            spyOn($, 'ajax');
            Cl.events._handler.call(
                $('.js-trigger')[1], this.preventEvent);

            var callArgs = $.ajax.calls.allArgs()[0][0];

            // validate ajax request url to have a proper year and month
            expect(callArgs.url).toEqual(
                '/en/events/get-dates/2015/8/?plugin_pk='
            );
        });

        it('has correct ajax request if direction is "next" and year is ' +
            '2015, month is 12', function () {
            spyOn($, 'ajax');
            Cl.events._handler.call(
                $('.js-trigger')[2], this.preventEvent);

            var callArgs = $.ajax.calls.allArgs()[0][0];

            // validate ajax request url to have a proper year and month
            expect(callArgs.url).toEqual(
                '/en/events/get-dates/2016/1/?plugin_pk='
            );
        });

        it('has correct ajax request if direction is "previous" and year is ' +
            '2015, month is 7', function () {
            spyOn($, 'ajax');
            Cl.events._handler.call(
                $('.js-trigger')[3], this.preventEvent);

            var callArgs = $.ajax.calls.allArgs()[0][0];

            // validate ajax request url to have a proper year and month
            expect(callArgs.url).toEqual(
                '/en/events/get-dates/2015/6/?plugin_pk='
            );
        });

        it('has correct ajax request if direction is "previous" and year is ' +
            '2015, month is 1', function () {
            spyOn($, 'ajax');
            Cl.events._handler.call(
                $('.js-trigger')[4], this.preventEvent);

            var callArgs = $.ajax.calls.allArgs()[0][0];

            // validate ajax request url to have a proper year and month
            expect(callArgs.url).toEqual(
                '/en/events/get-dates/2014/12/?plugin_pk='
            );
        });

        it('has correct ajax request if data-pk is specified', function () {
            spyOn($, 'ajax');
            Cl.events._handler.call(
                $('.js-trigger')[5], this.preventEvent);

            var callArgs = $.ajax.calls.allArgs()[0][0];

            // validate ajax request url to have a proper year and month
            expect(callArgs.url).toEqual(
                '/en/events/get-dates/2014/12/?plugin_pk=test1'
            );
        });

        it('has ajax request with "success" function replacing the table ' +
            'class correctly', function () {
            spyOn($, 'ajax').and.callFake(function (params) {
                params.success('<table class="test-table" data-month' +
                    '="Testmonth" data-year="2020"></table>');
            });

            Cl.events._handler.call(
                $('.js-trigger')[5], this.preventEvent);

            // validate that "table-calendar" tables got reduced by 1
            expect($('.table-calendar').length).toEqual(4);
            // validate that the table with class "test-table" appeared
            expect($('.test-table').length).toEqual(1);

            // validate that h3 title gets updated with new month and year
            expect($('h3')[4].innerHTML).toEqual('Testmonth 2020');
        });

        it('has ajax request with "error" function alert working ' +
            'correctly', function () {
            spyOn($, 'ajax').and.callFake(function (params) {
                params.error();
            });

            spyOn(window, 'alert');

            Cl.events._handler.call(
                $('.js-trigger')[5], this.preventEvent);

            expect(window.alert).toHaveBeenCalledWith('Test: There was a ' +
                'problem accessing the calendar, please try again.');
        });
    });

});
