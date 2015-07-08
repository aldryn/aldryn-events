/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

'use strict';
/* global describe, it, browser */

// #############################################################################
// INTEGRATION TEST
describe('Aldryn Events tests: ', function () {
    var aldrynEventsPage = require('../pages/page.add.delete.event.js');

    it('login to the site with valid username and password', function () {
        // go to the main page
        browser.get(aldrynEventsPage.site);

        // click edit mode link
        aldrynEventsPage.editModeLink.click();

        // wait for username input to appear
        browser.wait(function () {
            return browser.isElementPresent(aldrynEventsPage.usernameInput);
        }, aldrynEventsPage.mainElementsWaitTime);

        // login to the site
        aldrynEventsPage.loginToSite(
            aldrynEventsPage.usernameInput,
            aldrynEventsPage.loginUsername,
            aldrynEventsPage.passwordInput,
            aldrynEventsPage.loginPassword,
            aldrynEventsPage.loginButton,
            aldrynEventsPage.userMenuOptions.first()
        );
    });
});
