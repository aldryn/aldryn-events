'use strict';

var helpers = require('djangocms-casper-helpers');
var globals = helpers.settings;
var casperjs = require('casper');
var cms = helpers(casperjs);
var xPath = casperjs.selectXPath;

casper.test.setUp(function (done) {
    casper.start()
        .then(cms.login())
        .run(done);
});

casper.test.tearDown(function (done) {
    casper.start()
        .then(cms.logout())
        .run(done);
});

casper.test.begin('Creation / deletion of the apphook', function (test) {
    casper
        .start(globals.adminUrl)
        .waitUntilVisible('#content', function () {
            test.assertVisible('#content', 'Admin loaded');
            this.click(
                xPath(cms.getXPathForAdminSection({
                    section: 'Aldryn Events',
                    row: 'Events configs',
                    link: 'Add'
                }))
            );
        })
        .waitForUrl(/add/)
        .waitUntilVisible('#eventsconfig_form')
        .then(function () {
            test.assertVisible('#eventsconfig_form', 'Apphook creation form loaded');

            this.fill('#eventsconfig_form', {
                namespace: 'Test namespace',
                app_title: 'Test Events'
            }, true);
        })
        .waitUntilVisible('.success', function () {
            test.assertSelectorHasText(
                '.success',
                'The events config "Events / Test Events" was added successfully.',
                'Apphook config was created'
            );

            test.assertElementCount(
                '#result_list tbody tr',
                2,
                'There are 2 apphooks now'
            );

            this.clickLabel('Events / Test Events', 'a');
        })
        .waitUntilVisible('.deletelink', function () {
            this.click('.deletelink');
        })
        .waitForUrl(/delete/, function () {
            this.click('input[value="Yes, I\'m sure"]');
        })
        .waitUntilVisible('.success', function () {
            test.assertSelectorHasText(
                '.success',
                'The events config "Events / Test Events" was deleted successfully.',
                'Apphook config was deleted'
            );
        })
        .run(function () {
            test.done();
        });
});

casper.test.begin('Creation / deletion of the event', function (test) {
    casper
        .start()
        .then(cms.addPage({ title: 'Events' }))
        .then(cms.addApphookToPage({
            page: 'Events',
            apphook: 'EventListAppHook'
        }))
        .then(cms.publishPage({
            page: 'Events'
        }))
        .thenOpen(globals.editUrl, function () {
            test.assertSelectorHasText('p', 'No items available', 'No events yet');
        })
        .thenOpen(globals.adminUrl)
        .waitUntilVisible('#content', function () {
            test.assertVisible('#content', 'Admin loaded');
            this.click(
                xPath(cms.getXPathForAdminSection({
                    section: 'Aldryn Events',
                    row: 'Events',
                    link: 'Add'
                }))
            );
        })
        .waitForUrl(/add/)
        .waitUntilVisible('#event_form')
        .then(function () {
            test.assertVisible('#event_form', 'Event creation form loaded');

            this.fill('#event_form', {
                title: 'Test event',
                start_date: '2100-07-09'
            }, true);
        })
        .waitUntilVisible('.success', function () {
            test.assertSelectorHasText(
                '.success',
                'The Event "Test event (Events)" was added successfully.',
                'Event was created'
            );

            test.assertElementCount(
                '#result_list tbody tr',
                1,
                'There is 1 event available'
            );
        })
        .thenOpen(globals.editUrl, function () {
            test.assertExists(
                '.js-calendar-table',
                'Calendar is available'
            );
            test.assertSelectorHasText(
                '.article.events-upcoming h2 a',
                'Test event',
                'Event is available on the page'
            );
        })
        .thenOpen(globals.adminUrl)
        .waitUntilVisible('#content', function () {
            this.click(
                xPath(cms.getXPathForAdminSection({
                    section: 'Aldryn Events',
                    row: 'Events'
                }))
            );
        })
        .waitForUrl(/events/, function () {
            this.clickLabel('Test event', 'a');
        })
        .waitUntilVisible('.deletelink', function () {
            this.click('.deletelink');
        })
        .waitForUrl(/delete/, function () {
            this.click('input[value="Yes, I\'m sure"]');
        })
        .waitUntilVisible('.success', function () {
            test.assertSelectorHasText(
                '.success',
                'The Event "Test event (Events)" was deleted successfully.',
                'Event was deleted'
            );
        })
        .then(cms.removePage())
        .run(function () {
            test.done();
        });
});

casper.test.begin('Upcoming events plugin', function (test) {
    casper
        .start()
        .then(cms.addPage({ title: 'Home' }))
        .then(cms.addPage({ title: 'Events' }))
        .then(cms.addApphookToPage({
            page: 'Events',
            apphook: 'EventListAppHook'
        }))
        .then(cms.publishPage({ page: 'Events' }))
        .thenOpen(globals.editUrl)
        .then(cms.addPlugin({
            type: 'UpcomingPlugin',
            content: {
                id_past_events: 'False',
                id_latest_entries: 1
            }
        }))
        .thenOpen(globals.editUrl, function () {
            test.assertSelectorHasText(
                '.cms-plugin li',
                'No items available',
                'No events yet'
            );
        })
        .wait(1000)
        .then(cms.openSideframe())
        // add events
        .withFrame(0, function () {
            this.waitForSelector('.cms-pagetree-breadcrumbs')
                .then(function () {
                    this.click('.cms-pagetree-breadcrumbs a:first-child');
                })
                .waitForUrl(/admin/)
                .waitForSelector('.dashboard', function () {
                    this.click(xPath(cms.getXPathForAdminSection({
                        section: 'Aldryn Events',
                        row: 'Events',
                        link: 'Add'
                    })));
                })
                .wait(1000)
                .waitForSelector('#event_form', function () {
                    this.fill('#event_form', {
                        title: 'Test event 2100',
                        start_date: '2100-07-09'
                    }, false);

                    this.click('input[value="Save and add another"]');
                })
                .wait(1000)
                .waitForSelector('.success', function () {
                    test.assertSelectorHasText(
                        '.success',
                        'The Event "Test event 2100 (Events)" was added successfully.',
                        'First event added'
                    );

                    this.fill('#event_form', {
                        title: 'Test event 2500',
                        start_date: '2500-07-09'
                    }, true);
                })
                .waitForSelector('.success')
                .wait(1000);
        })
        .thenOpen(globals.editUrl, function () {
            test.assertDoesntExist(
                '.js-calendar-table',
                'Calendar is not available'
            );
            test.assertSelectorHasText(
                '.cms-plugin li a',
                'Test event 2100',
                'Closest event is visible on the page'
            );
            test.assertElementCount(
                '.cms-plugin li',
                1,
                'Only one event is visible on the page'
            );
        })
        // remove events
        .then(cms.openSideframe())
        .withFrame(0, function () {
            this.waitForSelector('.cms-pagetree-breadcrumbs')
                .then(function () {
                    this.click('.cms-pagetree-breadcrumbs a:first-child');
                })
                .waitForUrl(/admin/)
                .waitForSelector('.dashboard', function () {
                    this.click(xPath(cms.getXPathForAdminSection({
                        section: 'Aldryn Events',
                        row: 'Events'
                    })));
                })
                .waitForSelector('#changelist-form', function () {
                    this.click('th input[type="checkbox"]');
                    this.fill('#changelist-form', {
                        action: 'delete_selected'
                    }, true);

                })
                .waitForSelector('.delete-confirmation', function () {
                    this.click('input[value="Yes, I\'m sure"]');
                })
                .waitForSelector('.success', function () {
                    test.assertSelectorHasText(
                        '.success',
                        'Successfully deleted 2 Events.',
                        'Events deleted'
                    );
                });
        })
        .then(cms.removePage())
        .then(cms.removePage())
        .run(function () {
            test.done();
        });
});
