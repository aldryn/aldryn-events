/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

'use strict';
/* global describe, it, expect, browser */

// #############################################################################
// INTEGRATION TEST
describe('Aldryn Events tests: ', function () {
    var aldrynEventsPage = require('../pages/page.aldryn.events.js');

    it('main page should have a title', function () {
        browser.get(aldrynEventsPage.site);

        expect(browser.getTitle()).toContain('Welcome to django CMS');
    });
});
