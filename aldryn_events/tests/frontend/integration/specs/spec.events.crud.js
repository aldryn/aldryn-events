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
    it('logs in to the site with valid username and password', function () {
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

    it('creates a new test page', function () {
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

    it('creates a new event', function () {
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

    it('adds a new event on the page', function () {
        // switch to default page content
        browser.switchTo().defaultContent();

        // click the Page link in the top menu
        eventsPage.userMenus.get(1).click().then(function () {
            // wait for top menu dropdown options to appear
            browser.wait(function () {
                return browser.isElementPresent(eventsPage.userMenuDropdown);
            }, eventsPage.mainElementsWaitTime);

            eventsPage.advancedSettingsOption.click();

            // wait for modal iframe to appear
            browser.wait(function () {
                return browser.isElementPresent(eventsPage.modalIframe);
            }, eventsPage.iframeWaitTime);

            // switch to modal iframe
            browser.switchTo()
                .frame(browser.findElement(By.css('.cms_modal-frame iframe')));

            // wait for Application select to appear
            browser.wait(function () {
                return browser.isElementPresent(eventsPage.applicationSelect);
            }, eventsPage.mainElementsWaitTime);

            // set Application
            eventsPage.applicationSelect.click();
            eventsPage.applicationSelect.sendKeys('Events').then(function () {
                eventsPage.applicationSelect.click();
            });

            // switch to default page content
            browser.switchTo().defaultContent();

            eventsPage.saveModalButton.click();
        }).then(function () {
            // wait for events calendar block to appear
            browser.wait(function () {
                return browser.isElementPresent(eventsPage.eventsCalendarBlock);
            }, eventsPage.mainElementsWaitTime);

            // validate event date and time block
            expect(eventsPage.eventMetaBlock.isDisplayed()).toBeTruthy();
            // validate events calendar block
            expect(eventsPage.eventsCalendarBlock.isDisplayed()).toBeTruthy();

            // click the link to go to the event page
            eventsPage.eventLink.click();
        }).then(function () {
            // wait for event date and time block to appear
            browser.wait(function () {
                return browser.isElementPresent(eventsPage.eventMetaBlock);
            }, eventsPage.mainElementsWaitTime);

            // validate event date and time block on event page
            expect(eventsPage.eventMetaBlock.isDisplayed()).toBeTruthy();
            // validate Back to Overview link
            expect(eventsPage.backToOverviewLink.isDisplayed()).toBeTruthy();
        });
    });

});
