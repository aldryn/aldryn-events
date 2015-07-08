/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

'use strict';
/* global by, element, browser, expect */

// #############################################################################
// INTEGRATION TEST PAGE OBJECT

var aldrynEventsPage = {
    site: 'http://127.0.0.1:8000/en/',
    mainElementsWaitTime: 12000,

    // log in, log out
    editModeLink: element(by.css('.inner a[href="/?edit"]')),
    loginUsername: 'admin',
    loginPassword: 'admin',
    usernameInput: element(by.id('id_cms-username')),
    passwordInput: element(by.id('id_cms-password')),
    loginButton: element(by.css('.cms_form-login input[type="submit"]')),
    userMenuOptions: element.all(by.css('.cms_toolbar-item-navigation li')),

    loginToSite: function (emailInput, email, passwordInput, password,
        loginButton, userMenu) {
        emailInput.clear();

        // fill in email field
        emailInput.sendKeys(email).then(function () {
            passwordInput.clear();

            // fill in password field
            passwordInput.sendKeys(password);
        }).then(function () {
            loginButton.click();

            // wait for user menu to appear
            browser.wait(function () {
                return browser.isElementPresent(userMenu);
            }, aldrynEventsPage.mainElementsWaitTime);

            // validate user menu
            expect(userMenu.isDisplayed()).toBeTruthy();
        });
    },

};

module.exports = aldrynEventsPage;
