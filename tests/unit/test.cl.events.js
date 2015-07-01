/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

// #####################################################################################################################
// #NAMESPACES#
// var Cl = window.Cl || {};
/* global describe, it, expect */

// #####################################################################################################################
// #TESTS#
(function () {
    'use strict';

    describe('cl.events.js', function () {
        it('Cl namespace is available', function () {
            expect(Cl).toBeDefined();
        });

        it('has a public methode calendar', function () {
            expect(Cl.events.calendar).toBeDefined();
        });
    });

})();
