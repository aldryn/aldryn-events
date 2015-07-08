/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

'use strict';
/* global by, element, browser, expect */

// #############################################################################
// INTEGRATION TEST PAGE OBJECT

var eventsPage = {
    site: 'http://127.0.0.1:8000/en/',
    mainElementsWaitTime: 12000,

    // log in, log out
    editModeLink: element(by.css('.inner a[href="/?edit"]')),
    usernameInput: element(by.id('id_cms-username')),
    passwordInput: element(by.id('id_cms-password')),
    loginButton: element(by.css('.cms_form-login input[type="submit"]')),
    userMenuOption: element.all(by.css(
        '.cms_toolbar-item-navigation li')).first(),

    cmsLogin: function (object) {
        // object can contain username and password, if not set it will
        // fallback to 'admin'
        eventsPage.usernameInput.clear();

        // fill in email field
        eventsPage.usernameInput.sendKeys(object.username || 'admin')
            .then(function () {
            eventsPage.passwordInput.clear();

            // fill in password field
            eventsPage.passwordInput.sendKeys(object.password || 'admin');
        }).then(function () {
            eventsPage.loginButton.click();

            // wait for user menu to appear
            browser.wait(function () {
                return browser.isElementPresent(eventsPage.userMenuOption);
            }, eventsPage.mainElementsWaitTime);

            // validate user menu
            expect(eventsPage.userMenuOption.isDisplayed()).toBeTruthy();
        });
    },

};

module.exports = eventsPage;
