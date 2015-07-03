/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

(function () {
    'use strict';

    // ########################################################################
    /* global Cl, describe, it, expect */

    // ########################################################################
    describe('cl.events.js:', function () {
        beforeEach(function () {
            fixture.setBase('frontend/fixtures');
            this.markup = fixture.load('calendar.html');
        });

        afterEach(function(){
            fixture.cleanup();
        });

        it('has available Cl namespace', function () {
            expect(Cl).toBeDefined();
        });

        it('has a public method calendar', function () {
            expect(Cl.events.calendar).toBeDefined();
        });

        it('Cl.events.init() returns undefined', function () {
            expect(Cl.events.init()).toEqual(undefined);
        });

        it('runs calendar() in Cl.events.init()', function () {
            spyOn(Cl.events, 'calendar');
            Cl.events.init();

            // validate that calendar was called inside Cl.events.init()
            expect(Cl.events.calendar).toHaveBeenCalled();
            // validate 5 calls as 5 calendars are specified in calendar.html
            expect(Cl.events.calendar.calls.count()).toEqual(5);
        });

        it('Cl.events._handler returns false if direction is not specified', function () {
            expect(Cl.events._handler.call(
                $('.js-trigger')[0],
                { preventDefault: function () {} })
            ).toEqual(false);
        });

        it('Cl.events._handler returns undefined if direction is "next" and month is 7', function () {
            expect(Cl.events._handler.call(
                $('.js-trigger')[1],
                { preventDefault: function () {} })
            ).toEqual(undefined);
        });

        it('Cl.events._handler returns undefined if direction is "next" and month is 12', function () {
            expect(Cl.events._handler.call(
                $('.js-trigger')[2],
                { preventDefault: function () {} })
            ).toEqual(undefined);
        });

        it('Cl.events._handler returns undefined if direction is "previous" and month is 7', function () {
            expect(Cl.events._handler.call(
                $('.js-trigger')[3],
                { preventDefault: function () {} })
            ).toEqual(undefined);
        });

        it('Cl.events._handler returns undefined if direction is "previous" and month is 1', function () {
            expect(Cl.events._handler.call(
                $('.js-trigger')[4],
                { preventDefault: function () {} })
            ).toEqual(undefined);
        });
    });

})();
