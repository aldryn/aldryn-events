/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

'use strict';
/* global browser */

// #############################################################################
// CONFIGURATION
var baseConf = require('./base.conf');
var aldrynTestsLibrary = require('./integration/pages/alteli.js');
var formatTaskName = baseConf.formatTaskName;
var browsers = baseConf.sauceLabsBrowsers;

var config = {
    // Capabilities to be passed to the webdriver instance.
    capabilities: {
        'browserName': 'phantomjs',
        'phantomjs.binary.path': require('phantomjs').path
    },

    onPrepare: function () {
        // Set browser window size
        aldrynTestsLibrary.setWindowSize(browser.params.browserConfig.width,
            browser.params.browserConfig.height);
        // Set Angular site flag
        browser.ignoreSynchronization = true;
        // Pre-create folders for reporting
        aldrynTestsLibrary.preCreateFolder(
            'aldryn_events/tests/frontend/integration/screenshots');
        aldrynTestsLibrary.preCreateFolder(
            'aldryn_events/tests/frontend/integration/reports');
        // Automatically store a screenshot at the end of each test
        aldrynTestsLibrary.storeScreenshot(
            'aldryn_events/tests/frontend/integration/screenshots/');
    },

    // Name of the process executing this capability.  Not used directly by
    // protractor or the browser, but instead pass directly to third parties
    // like SauceLabs as the name of the job running this test
    name: 'aldryn-events',

    // Params for setting browser window width and height - can be also
    // changed via the command line as: --params.browserConfig.width 1024
    params: {
        browserConfig: {
            // to enable setting window width and height
            width: 1280,
            height: 1024
        }
    },

    // If set, protractor will save the test output in .json at this path.
    resultJsonOutputFile:
      'aldryn_events/tests/frontend/integration/reports/results.json',

    framework: 'jasmine2',

    jasmineNodeOpts: {
        isVerbose: true,
        showColors: true,
        defaultTimeoutInterval: 240000
    }

};

if (process.env.CI || process.env.SAUCE_USERNAME && process.env.SAUCE_ACCESS_KEY) {
    config.capabilities = null;
    config.sauceUser = process.env.SAUCE_USERNAME;
    config.sauceKey = process.env.SAUCE_ACCESS_KEY;
    config.multiCapabilities = Object.keys(browsers).map(function (key) {
        var browserCapability =  browsers[key];
        browserCapability.name = formatTaskName(browserCapability.browserName);
        return browserCapability;
    });
}

exports.config = config;
