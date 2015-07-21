/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

'use strict';
/* global describe, it, browser, protractor, By, expect, element */

// #############################################################################
// INTEGRATION TEST
var eventsPage = require('../pages/page.events.crud.js');

describe('Aldryn Events tests: ', function () {
    // create random event name
    var eventName = 'Test event ' + (Math.floor(Math.random() * 10001));

    it('logs in to the site with valid username and password', function () {
        // go to the main page
        browser.get(eventsPage.site);

        // check if the page already exists
        eventsPage.testLink.isPresent().then(function (present) {
            if (present === true) {
                // go to the main page
                browser.get(eventsPage.site + '?edit');
            } else {
                // click edit mode link
                eventsPage.editModeLink.click();
            }

            // wait for username input to appear
            browser.wait(function () {
                return browser.isElementPresent(eventsPage.usernameInput);
            }, eventsPage.mainElementsWaitTime);

            // login to the site
            eventsPage.cmsLogin();
        });
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

            // switch to sidebar menu iframe
            browser.switchTo().frame(browser.findElement(
                By.css('.cms_sideframe-frame iframe')));

            browser.wait(function () {
                return browser.isElementPresent(eventsPage.pagesLink);
            }, eventsPage.mainElementsWaitTime);

            eventsPage.pagesLink.click();

            // check if the page already exists and return the status
            return eventsPage.addPageLink.isPresent();
        }).then(function (present) {
            if (present === true) {
                // page is absent - create new page
                browser.wait(function () {
                    return browser.isElementPresent(eventsPage.addPageLink);
                }, eventsPage.mainElementsWaitTime);

                eventsPage.addPageLink.click();

                browser.wait(function () {
                    return browser.isElementPresent(eventsPage.titleInput);
                }, eventsPage.mainElementsWaitTime);

                eventsPage.titleInput.sendKeys('Test').then(function () {
                    eventsPage.saveButton.click();

                    eventsPage.slugErrorNotification.isPresent();
                }).then(function (present) {
                    if (present === false) {
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
                        eventsPage.testLink.getText()
                            .then(function (title) {
                            expect(title).toEqual('Test');
                        });
                    }
                });
            }
        });
    });

    it('creates a new apphook config', function () {
        // check if the focus is on sidebar ifarme
        eventsPage.editPageLink.isPresent().then(function (present) {
            if (present === false) {
                // wait for modal iframe to appear
                browser.wait(function () {
                    return browser.isElementPresent(eventsPage.sideMenuIframe);
                }, eventsPage.iframeWaitTime);

                // switch to sidebar menu iframe
                browser.switchTo().frame(browser.findElement(By.css(
                    '.cms_sideframe-frame iframe')));
            }
        }).then(function () {
            browser.wait(function () {
                return browser.isElementPresent(eventsPage.breadcrumbsLinks.first());
            }, eventsPage.mainElementsWaitTime);

            // click the Home link in breadcrumbs
            eventsPage.breadcrumbsLinks.first().click();

            browser.wait(function () {
                return browser.isElementPresent(eventsPage.eventsConfigsLink);
            }, eventsPage.mainElementsWaitTime);

            eventsPage.eventsConfigsLink.click();

            // check if the apphook config already exists and return the status
            return eventsPage.editEventsConfigsLink.isPresent();
        }).then(function (present) {
            if (present === false) {
                // apphook config is absent - create new apphook config
                browser.wait(function () {
                    return browser.isElementPresent(eventsPage.addEventsConfigsButton);
                }, eventsPage.mainElementsWaitTime);

                eventsPage.addEventsConfigsButton.click();

                browser.wait(function () {
                    return browser.isElementPresent(eventsPage.namespaceInput);
                }, eventsPage.mainElementsWaitTime);

                eventsPage.namespaceInput.sendKeys('aldryn_events')
                    .then(function () {
                    eventsPage.saveButton.click();

                    browser.wait(function () {
                        return browser.isElementPresent(eventsPage.editEventsConfigsLink);
                    }, eventsPage.mainElementsWaitTime);
                });
            }
        });
    });

    it('creates a new event', function () {
        browser.wait(function () {
            return browser.isElementPresent(eventsPage.breadcrumbsLinks.first());
        }, eventsPage.mainElementsWaitTime);

        // click the Home link in breadcrumbs
        eventsPage.breadcrumbsLinks.first().click();

        browser.wait(function () {
            return browser.isElementPresent(eventsPage.addEventLink);
        }, eventsPage.mainElementsWaitTime);

        eventsPage.addEventLink.click();

        var EC = protractor.ExpectedConditions;

        browser.wait(EC.and(
            EC.presenceOf(eventsPage.titleInput),
            EC.presenceOf(eventsPage.startDateLinks.first()),
            EC.presenceOf(eventsPage.startTimeLinks.first()),
            EC.presenceOf(element(By.css('#cke_id_short_description')))
        ), eventsPage.mainElementsWaitTime);

        eventsPage.titleInput.sendKeys(eventName).then(function () {
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
        eventsPage.eventsCalendarBlock.isPresent().then(function (present) {
            if (present === false) {
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
                    browser.switchTo().frame(browser.findElement(By.css(
                        '.cms_modal-frame iframe')));

                    // wait for Application select to appear
                    browser.wait(function () {
                        return browser.isElementPresent(eventsPage.applicationSelect);
                    }, eventsPage.mainElementsWaitTime);

                    // set Application
                    eventsPage.applicationSelect.click();
                    eventsPage.applicationSelect.sendKeys('Events')
                        .then(function () {
                        eventsPage.applicationSelect.click();
                    });

                    // switch to default page content
                    browser.switchTo().defaultContent();

                    browser.wait(function () {
                        return browser.isElementPresent(eventsPage.saveModalButton);
                    }, eventsPage.mainElementsWaitTime);

                    browser.actions().mouseMove(eventsPage.saveModalButton)
                        .perform();
                    eventsPage.saveModalButton.click();
                }).then(function () {
                    // wait for event date and time block to appear
                    browser.wait(function () {
                        return browser.isElementPresent(eventsPage.eventMetaBlock);
                    }, eventsPage.mainElementsWaitTime);

                    // validate event date and time block
                    expect(eventsPage.eventMetaBlock.isDisplayed())
                        .toBeTruthy();
                    // validate events calendar block
                    expect(eventsPage.eventsCalendarBlock.isDisplayed())
                        .toBeTruthy();

                    // click the link to go to the event page
                    eventsPage.eventLink.click();
                }).then(function () {
                    // wait for event date and time block to appear
                    browser.wait(function () {
                        return browser.isElementPresent(eventsPage.eventMetaBlock);
                    }, eventsPage.mainElementsWaitTime);

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
        // wait for modal iframe to appear
        browser.wait(function () {
            return browser.isElementPresent(eventsPage.sideMenuIframe);
        }, eventsPage.iframeWaitTime);

        // switch to sidebar menu iframe
        browser.switchTo()
            .frame(browser.findElement(By.css('.cms_sideframe-frame iframe')));

        // wait for edit event link to appear
        browser.wait(function () {
            return browser.isElementPresent(eventsPage.editEventLinks.first());
        }, eventsPage.mainElementsWaitTime);

        // validate edit event links texts to find proper event for deletion
        eventsPage.editEventLinks.first().getText().then(function (text) {
            if (text === eventName) {
                eventsPage.editEventLinks.first().click();
            } else {
                eventsPage.editEventLinks.get(1).getText()
                    .then(function (text) {
                    if (text === eventName) {
                        eventsPage.editEventLinks.get(1).click();
                    } else {
                        eventsPage.editEventLinks.get(2).getText()
                            .then(function (text) {
                            if (text === eventName) {
                                eventsPage.editEventLinks.get(2).click();
                            }
                        });
                    }
                });
            }
        }).then(function () {
            // wait for delete button to appear
            browser.wait(function () {
                return browser.isElementPresent(eventsPage.deleteButton);
            }, eventsPage.mainElementsWaitTime);

            eventsPage.deleteButton.click();

            // wait for confirmation button to appear
            browser.wait(function () {
                return browser.isElementPresent(eventsPage.sidebarConfirmationButton);
            }, eventsPage.mainElementsWaitTime);

            eventsPage.sidebarConfirmationButton.click();

            browser.wait(function () {
                return browser.isElementPresent(eventsPage.successNotification);
            }, eventsPage.mainElementsWaitTime);

            // validate success notification
            expect(eventsPage.successNotification.isDisplayed()).toBeTruthy();

            // switch to default page content
            browser.switchTo().defaultContent();

            // refresh the page to see changes
            browser.refresh();
        });
    });

});
