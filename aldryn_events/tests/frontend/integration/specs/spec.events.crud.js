/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

'use strict';
/* global describe, it, browser, By, expect */

// #############################################################################
// INTEGRATION TEST
var eventsPage = require('../pages/page.events.crud.js');

describe('Aldryn Events tests: ', function () {
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
        eventsPage.cmsLogin();
    });

    it('create a new test page', function () {
        // click the example.com link in the top menu
        eventsPage.userMenus.first().click().then(function () {
            // wait for top menu dropdown options to appear
            browser.wait(function () {
                return browser.isElementPresent(eventsPage.userMenuDropdown);
            }, eventsPage.mainElementsWaitTime);

            eventsPage.administrationOptions.first().click();
        }).then(function () {
            // wait for modal iframe to appear
            browser.wait(function () {
                return browser.isElementPresent(eventsPage.sideMenuIframe);
            }, eventsPage.iframeWaitTime);

            // switch to side menu iframe
            browser.switchTo()
                .frame(browser.findElement(By.css('.cms_sideframe-frame iframe')));

            browser.wait(function () {
                return browser.isElementPresent(eventsPage.addPageLink);
            }, eventsPage.mainElementsWaitTime);

            eventsPage.addPageLink.click();

            browser.wait(function () {
                return browser.isElementPresent(eventsPage.pageTitleInput);
            }, eventsPage.mainElementsWaitTime);

            eventsPage.pageTitleInput.sendKeys('Test');
        }).then(function () {
            eventsPage.saveButton.click();

            browser.wait(function () {
                return browser.isElementPresent(eventsPage.editPageLink);
            }, eventsPage.mainElementsWaitTime);

            eventsPage.editPageLink.click();

            // switch to default page content
            browser.switchTo().defaultContent();

            browser.wait(function () {
                return browser.isElementPresent(eventsPage.testLink);
            }, eventsPage.mainElementsWaitTime);

            // validate test link text
            eventsPage.testLink.getText()
            .then(function (title) {
                expect(title).toEqual('Test');
            });
        });
    });
});
