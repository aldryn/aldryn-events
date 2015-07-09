/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

'use strict';
/* global by, element, browser, expect */

// #############################################################################
// INTEGRATION TEST PAGE OBJECT

var eventsPage = {
    site: '/',
    mainElementsWaitTime: 12000,
    iframeWaitTime: 15000,

    // log in, log out
    editModeLink: element(by.css('.inner a[href="/?edit"]')),
    usernameInput: element(by.id('id_cms-username')),
    passwordInput: element(by.id('id_cms-password')),
    loginButton: element(by.css('.cms_form-login input[type="submit"]')),
    userMenus: element.all(by.css('.cms_toolbar-item-navigation li')),
    userMenuDropdown: element(by.css(
        '.cms_toolbar-item-navigation-hover')),
    administrationOptions: element.all(by.css(
        '.cms_toolbar-item-navigation a[href="/en/admin/"]')),
    sideMenuIframe: element(by.css('.cms_sideframe-frame iframe')),
    addPageLink: element(by.css('.model-page .addlink')),
    pageTitleInput: element(by.id('id_title')),
    saveButton: element(by.css('.submit-row [name="_save"]')),
    editPageLink: element(by.css('.col1 a')),
    testLink: element(by.css('.selected a')),

    cmsLogin: function (credentials) {
        // object can contain username and password, if not set it will
        // fallback to 'admin'
        credentials = credentials ||
            { username: 'admin', password: 'admin' };

        eventsPage.usernameInput.clear();

        // fill in email field
        eventsPage.usernameInput.sendKeys(
            credentials.username).then(function () {
            eventsPage.passwordInput.clear();

            // fill in password field
            eventsPage.passwordInput.sendKeys(
                credentials.password);
        }).then(function () {
            eventsPage.loginButton.click();

            // wait for user menu to appear
            browser.wait(function () {
                return browser.isElementPresent(eventsPage.userMenus.first());
            }, eventsPage.mainElementsWaitTime);

            // validate user menu
            expect(eventsPage.userMenus.first().isDisplayed())
                .toBeTruthy();
        });
    },

};

module.exports = eventsPage;
