/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

'use strict';

// #####################################################################################################################
// #NAMESPACES#
/* global Cl, describe, it, expect */

// #####################################################################################################################
// #UNIT TEST#
describe('cl.events.js', function () {
    it('Cl namespace is available', function () {
        expect(Cl).toBeDefined();
    });

    it('has a public methode calendar', function () {
        expect(Cl.events.calendar).toBeDefined();
    });
});
