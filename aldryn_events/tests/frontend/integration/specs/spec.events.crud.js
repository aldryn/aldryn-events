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
            browser.switchTo().frame(browser.findElement(
                By.css('.cms_sideframe-frame iframe')));

            browser.wait(function () {
                return browser.isElementPresent(eventsPage.addPageLink);
            }, eventsPage.mainElementsWaitTime);

            eventsPage.addPageLink.click();

            browser.wait(function () {
                return browser.isElementPresent(eventsPage.titleInput);
            }, eventsPage.mainElementsWaitTime);

            eventsPage.titleInput.sendKeys('Test');
        }).then(function () {
            eventsPage.saveButton.click();

            browser.wait(function () {
                return browser.isElementPresent(eventsPage.editPageLink);
            }, eventsPage.mainElementsWaitTime);

            // validate/click edit page link
            eventsPage.editPageLink.click();

            // switch to default page content
            browser.switchTo().defaultContent();

            browser.wait(function () {
                return browser.isElementPresent(eventsPage.testLink);
            }, eventsPage.mainElementsWaitTime);

            // validate test link text
            eventsPage.testLink.getText().then(function (title) {
                expect(title).toEqual('Test');
            });
        });
    });

    it('create a new event', function () {
        // wait for modal iframe to appear
        browser.wait(function () {
            return browser.isElementPresent(eventsPage.sideMenuIframe);
        }, eventsPage.iframeWaitTime);

        // switch to side menu iframe
        browser.switchTo()
            .frame(browser.findElement(By.css('.cms_sideframe-frame iframe')));

        browser.wait(function () {
            return browser.isElementPresent(eventsPage.breadcrumbsLinks.first());
        }, eventsPage.mainElementsWaitTime);

        // click the Home link in breadcrumbs
        eventsPage.breadcrumbsLinks.first().click();

        browser.wait(function () {
            return browser.isElementPresent(eventsPage.addEventLink);
        }, eventsPage.mainElementsWaitTime);

        eventsPage.addEventLink.click();

        browser.wait(function () {
            return browser.isElementPresent(eventsPage.titleInput);
        }, eventsPage.mainElementsWaitTime);

        eventsPage.titleInput.sendKeys('Test event').then(function () {
            // click Today link
            eventsPage.startDateLinks.first().click();
            // click Now link
            eventsPage.startTimeLinks.first().click();
            // set End date
            eventsPage.endDateInput.sendKeys('2100-07-09');
            // set End time
            eventsPage.endTimeInput.sendKeys('12:34:56');
        }).then(function () {
            eventsPage.saveButton.click();

            browser.wait(function () {
                return browser.isElementPresent(eventsPage.successNotification);
            }, eventsPage.mainElementsWaitTime);

            // validate success notification
            expect(eventsPage.successNotification.isDisplayed()).toBeTruthy();
            // validate edit event link
            expect(eventsPage.editEventLink.isDisplayed()).toBeTruthy();
        });
    });

});
