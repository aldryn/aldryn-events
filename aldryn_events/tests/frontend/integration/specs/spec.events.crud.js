/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

'use strict';
/* global describe, it, browser */

// #############################################################################
// INTEGRATION TEST
describe('Aldryn Events tests: ', function () {
    var eventsPage = require('../pages/page.events.crud.js');

    it('login to the site with valid username and password', function () {
        // go to the main page
        browser.get(eventsPage.site);

        // click edit mode link
        eventsPage.editModeLink.click();

        // wait for username input to appear
        browser.wait(function () {
            return browser.isElementPresent(eventsPage.usernameInput);
        }, eventsPage.mainElementsWaitTime);

        // login to the site
        eventsPage.cmsLogin({});
    });
});
