/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

'use strict';
/* global describe, it, browser, protractor, By, expect, element */

// #############################################################################
// INTEGRATION TEST
var eventsPage = require('../pages/page.events.crud.js');
var cmsProtractorHelper = require('cms-protractor-helper');

describe('Aldryn Events tests: ', function () {
    // create random event name
    var eventName = 'Test event ' + cmsProtractorHelper.randomDigits(4);

    it('logs in to the site with valid username and password', function () {
        // go to the main page
        browser.get(eventsPage.site);

        // check if the page already exists
        eventsPage.testLink.isPresent().then(function (present) {
            if (present === true) {
                // go to the main page
                browser.get(eventsPage.site + '?edit');
                browser.sleep(1000);
                cmsProtractorHelper.waitForDisplayed(eventsPage.usernameInput);
            }

            // login to the site
            eventsPage.cmsLogin();
        });
    });

    it('creates a new test page', function () {
        // close the wizard if necessary
        eventsPage.modalCloseButton.isDisplayed().then(function (displayed) {
            if (displayed) {
                eventsPage.modalCloseButton.click();
            }
        });

        cmsProtractorHelper.waitForDisplayed(eventsPage.userMenus.first());
        // have to wait till animation finished
        browser.sleep(300);

        // click the example.com link in the top menu
        return eventsPage.userMenus.first().click().then(function () {
            // wait for top menu dropdown options to appear
            cmsProtractorHelper.waitFor(eventsPage.userMenuDropdown);

            return eventsPage.administrationOptions.first().click();
        }).then(function () {
            // wait for modal iframe to appear
            cmsProtractorHelper.waitFor(eventsPage.sideMenuIframe);

            // switch to sidebar menu iframe
            browser.switchTo().frame(browser.findElement(
                By.css('.cms-sideframe-frame iframe')));

            cmsProtractorHelper.waitFor(eventsPage.pagesLink);

            eventsPage.pagesLink.click();

            // wait for iframe side menu to reload
            cmsProtractorHelper.waitFor(eventsPage.addEventsConfigsButton);

            // check if the page already exists and return the status
            return eventsPage.addPageLink.isPresent();
        }).then(function (present) {
            if (present === true) {
                // page is absent - create new page
                cmsProtractorHelper.waitFor(eventsPage.addPageLink);

                eventsPage.addPageLink.click();

                cmsProtractorHelper.waitFor(eventsPage.titleInput);

                return eventsPage.titleInput.sendKeys('Test').then(function () {
                    eventsPage.saveButton.click();

                    return eventsPage.slugErrorNotification.isPresent();
                }).then(function (present) {
                    if (present === false) {
                        cmsProtractorHelper.waitFor(eventsPage.editPageLink);

                        // wait till the editPageLink will become clickable
                        browser.sleep(500);

                        // validate/click edit page link
                        eventsPage.editPageLink.click();

                        // switch to default page content
                        browser.switchTo().defaultContent();

                        cmsProtractorHelper.waitFor(eventsPage.testLink);

                        // validate test link text
                        return eventsPage.testLink.getText().then(function (title) {
                            expect(title).toEqual('Test');
                        });
                    }
                });
            }
        });
    });

    it('creates a new apphook config', function () {
        // check if the focus is on sidebar ifarme
        return eventsPage.editPageLink.isPresent().then(function (present) {
            if (present === false) {
                // wait for modal iframe to appear
                cmsProtractorHelper.waitFor(eventsPage.sideMenuIframe);

                // switch to sidebar menu iframe
                return browser.switchTo().frame(browser.findElement(By.css(
                    '.cms-sideframe-frame iframe')));
            }
        }).then(function () {
            browser.sleep(1000);

            eventsPage.breadcrumbs.isPresent().then(function (present) {
                if (present) {
                    // click the Home link in breadcrumbs
                    cmsProtractorHelper.waitFor(eventsPage.breadcrumbsLinks.first());
                    eventsPage.breadcrumbsLinks.first().click();
                }
            });

            cmsProtractorHelper.waitFor(eventsPage.eventsConfigsLink);

            eventsPage.eventsConfigsLink.click();

            // check if the apphook config already exists and return the status
            return eventsPage.editEventsConfigsLink.isPresent();
        }).then(function (present) {
            if (present === false) {
                // apphook config is absent - create new apphook config
                cmsProtractorHelper.waitFor(eventsPage.addEventsConfigsButton);

                eventsPage.addEventsConfigsButton.click();

                cmsProtractorHelper.waitFor(eventsPage.namespaceInput);

                return eventsPage.namespaceInput.sendKeys('custom_aldryn_events')
                    .then(function () {
                    return eventsPage.applicationTitleInput.sendKeys('Test application');
                }).then(function () {
                    eventsPage.saveButton.click();

                    cmsProtractorHelper.waitFor(eventsPage.editEventsConfigsLink);
                });
            }
        });
    });

    it('creates a new event', function () {
        cmsProtractorHelper.waitFor(eventsPage.breadcrumbsLinks.first());

        // click the Home link in breadcrumbs
        eventsPage.breadcrumbsLinks.first().click();

        cmsProtractorHelper.waitFor(eventsPage.addEventLink);

        eventsPage.addEventLink.click();

        var EC = protractor.ExpectedConditions;

        browser.wait(EC.and(
            EC.presenceOf(eventsPage.titleInput),
            EC.presenceOf(eventsPage.startDateLinks.first()),
            EC.presenceOf(eventsPage.startTimeLinks.first()),
            EC.presenceOf(element(By.css('#cke_id_short_description')))
        ), cmsProtractorHelper.mainElementsWaitTime);

        return eventsPage.titleInput.sendKeys(eventName).then(function () {
            // click Today link
            eventsPage.startDateLinks.first().click();
            // click Now link
            eventsPage.startTimeLinks.first().click();
            // set End date
            eventsPage.endDateInput.sendKeys('2100-07-09');
            // set End time
            return eventsPage.endTimeInput.sendKeys('12:34:56');
        }).then(function () {
            eventsPage.saveButton.click();

            cmsProtractorHelper.waitFor(eventsPage.successNotification);

            // validate success notification
            expect(eventsPage.successNotification.isDisplayed())
                .toBeTruthy();
            // validate edit event link
            expect(eventsPage.editEventLinks.first().isDisplayed())
                .toBeTruthy();
        });
    });

    it('adds a new event on the page', function () {
        // switch to default page content
        browser.switchTo().defaultContent();

        // add events to the page only if they were not added before
        return eventsPage.eventsCalendarBlock.isPresent().then(function (present) {
            if (present === false) {
                // click the Page link in the top menu
                eventsPage.userMenus.get(1).click().then(function () {
                    // wait for top menu dropdown options to appear
                    cmsProtractorHelper.waitFor(eventsPage.userMenuDropdown);

                    eventsPage.advancedSettingsOption.click();

                    // wait for modal iframe to appear
                    cmsProtractorHelper.waitFor(eventsPage.modalIframe);

                    // switch to modal iframe
                    browser.switchTo().frame(browser.findElement(By.css(
                        '.cms-modal-frame iframe')));

                    cmsProtractorHelper.selectOption(eventsPage.applicationSelect,
                        'Events', eventsPage.eventsOption);

                    // switch to default page content
                    browser.switchTo().defaultContent();

                    cmsProtractorHelper.waitFor(eventsPage.saveModalButton);

                    browser.actions().mouseMove(eventsPage.saveModalButton)
                        .perform();
                    return eventsPage.saveModalButton.click();
                }).then(function () {
                    // wait for event date and time block to appear
                    cmsProtractorHelper.waitFor(eventsPage.eventMetaBlock);

                    // validate event date and time block
                    expect(eventsPage.eventMetaBlock.isDisplayed())
                        .toBeTruthy();
                    // validate events calendar block
                    expect(eventsPage.eventsCalendarBlock.isDisplayed())
                        .toBeTruthy();

                    // wait till animation of sideframe opening finishes
                    browser.sleep(300);

                    // close sideframe (it covers the link)
                    cmsProtractorHelper.waitFor(eventsPage.sideFrameClose);
                    eventsPage.sideFrameClose.click();

                    // wait till animation finishes
                    browser.sleep(300);

                    // click the link to go to the event page
                    return eventsPage.eventLink.click();
                }).then(function () {
                    // wait for event date and time block to appear
                    cmsProtractorHelper.waitFor(eventsPage.eventMetaBlock);

                    // validate event date and time block on event page
                    expect(eventsPage.eventMetaBlock.isDisplayed())
                        .toBeTruthy();
                    // validate Back to Overview link
                    expect(eventsPage.backToOverviewLink.isDisplayed())
                        .toBeTruthy();

                    eventsPage.backToOverviewLink.click();
                });
            }
        });
    });

    it('deletes event', function () {
        // have to wait till animation finished
        browser.sleep(300);
        // click the example.com link in the top menu
        eventsPage.userMenus.first().click().then(function () {
            // wait for top menu dropdown options to appear
            cmsProtractorHelper.waitForDisplayed(eventsPage.userMenuDropdown);

            return eventsPage.administrationOptions.first().click();
        }).then(function () {
            // wait for modal iframe to appear
            cmsProtractorHelper.waitFor(eventsPage.sideMenuIframe);
        });

        // switch to sidebar menu iframe
        browser.switchTo()
            .frame(browser.findElement(By.css('.cms-sideframe-frame iframe')));

        // browser.pause();
        cmsProtractorHelper.waitFor(eventsPage.editEventLink);
        browser.sleep(100);
        eventsPage.editEventLink.click().then(function () {
            // wait for edit event link to appear
            return cmsProtractorHelper.waitFor(eventsPage.editEventLinksTable);
        }).then(function () {
            // validate edit event links texts to delete proper event
            return eventsPage.editEventLinks.first().getText();
        }).then(function (text) {
            if (text === eventName) {
                return eventsPage.editEventLinks.first().click();
            } else {
                return eventsPage.editEventLinks.get(1).getText()
                    .then(function (text) {
                    if (text === eventName) {
                        return eventsPage.editEventLinks.get(1).click();
                    } else {
                        return eventsPage.editEventLinks.get(2).getText()
                            .then(function (text) {
                            if (text === eventName) {
                                return eventsPage.editEventLinks.get(2).click();
                            }
                        });
                    }
                });
            }
        }).then(function () {
            // wait for delete button to appear
            cmsProtractorHelper.waitFor(eventsPage.deleteButton);

            // move the mouse and scroll the screen to deleteButton
            browser.actions().mouseMove(eventsPage.deleteButton).perform();
            eventsPage.deleteButton.click();

            // wait for confirmation button to appear
            cmsProtractorHelper.waitFor(eventsPage.sidebarConfirmationButton);

            eventsPage.sidebarConfirmationButton.click();

            cmsProtractorHelper.waitFor(eventsPage.successNotification);

            // validate success notification
            expect(eventsPage.successNotification.isDisplayed()).toBeTruthy();

            // switch to default page content
            browser.switchTo().defaultContent();

            // refresh the page to see changes
            browser.refresh();
        });
    });

});
