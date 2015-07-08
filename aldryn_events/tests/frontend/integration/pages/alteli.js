// ALDRYN TESTS LIBRARY
// ############################################################################
'use strict';
/* global expect, browser, jasmine */
/* jshint browser: true */
/* jshint shadow: true */

var aldrynTestsLibrary = {
    // utility to set browser window size
    setWindowSize: function (width, height) {
        browser.driver.manage().window().setSize(
            width,
            height
        );
    },

    // utility to pre-create folder with 0777 permissions
    preCreateFolder: function (folderName) {
        var fs = require('fs');
        var path = require('path');

        var mkdirSync = function (path, mode) {
            try {
                fs.mkdirSync(path, mode);
            } catch (e) {
                if (e.code !== 'EEXIST') {
                    throw e;
                }
            }
        };
        mkdirSync(path.join(folderName), 511);
    },

    // utility to automatically store a screenshot at the end of each test
    storeScreenshot: function (screenShotDirectoryPath) {
        // screenshots creation
        var fs = require('fs');
        var screenShotDirectory = screenShotDirectoryPath;
        var Utils = {
            /**
             * @name writeScreenShot
             * @description Write a screenshot string to file.
             * @param {String} data The base64-encoded string to write to file
             * @param {String} filename The name of the file to create (do not
             * specify directory)
             */
            writeScreenShot: function (data, filename) {
                var stream = fs.createWriteStream(
                    screenShotDirectory + filename
                );

                stream.write(new Buffer(data, 'base64'));
                stream.end();
            }
        };

        jasmine.getEnv().addReporter({
            specDone: function (result) {
                browser.getCapabilities().then(function (capabilities) {
                    browser.takeScreenshot().then(function (png) {
                        var browserName = capabilities.caps_.browserName;
                        var filename =
                        browserName + '-' +
                        result.status.toUpperCase() + '-' +
                        result.fullName.replace(/ /g, '_') + '.png';

                        Utils.writeScreenShot(png, filename);
                    });
                });
            }
        });
    },

    // utility to test expectation an element is missing
    expectByCssToBeAbsent: function (element) {
        element.isPresent().then(function (present) {
            expect(present).toBeFalsy();
        });
    },

    setEmail: function (emailInput, email) {
        emailInput.clear().then(function () {
            emailInput.sendKeys(email);
        });
    },
    setPassword: function (passwordInput, password) {
        passwordInput.clear().then(function () {
            passwordInput.sendKeys(password);
        });
    },

    loginToSite: function (
        emailInput,
        email,
        passwordInput,
        password,
        loginButton,
        userMenu
        ) {
        emailInput.clear().then(function () {
            // fill in email field
            emailInput.sendKeys(email).then(function () {
                passwordInput.clear().then(function () {
                    // fill in password field
                    passwordInput.sendKeys(password).then(function () {
                        loginButton.click();

                        browser.wait(function () {
                            return browser.isElementPresent(userMenu);
                        }, 8000);

                        // validate user menu
                        expect(userMenu.isDisplayed()).toBeTruthy();
                    });
                });
            });
        });
    },

    switchToNewTab: function (newTabURL) {
        browser.getAllWindowHandles().then(function (handles) {
            var newWindowHandle = handles[1];

            // put the focus on the second tab
            return browser.switchTo().window(newWindowHandle);
        }).then(function () {
            // validate new tab url
            expect(browser.driver.getCurrentUrl()).toContain(newTabURL);
        });
    },

    switchToOldTab: function (closeOldTab) {
        browser.getAllWindowHandles().then(function (handles) {
            var oldWindowHandle = handles[0];

            if (closeOldTab) {
                // close current tab
                browser.close().then(function () {
                    // switch to the old tab
                    browser.switchTo().window(oldWindowHandle);
                });
            } else {
                // switch to the old tab
                browser.switchTo().window(oldWindowHandle);
            }
        });
    },

    logoutFromSite: function (userDropdownMenu, logoutLink, loginButton) {
        browser.wait(function () {
            return browser.isElementPresent(userDropdownMenu);
        }, 8000);

        // click the user dropdown menu and logout link
        userDropdownMenu.click();
        logoutLink.click();

        // validate login button
        expect(loginButton.isDisplayed()).toBeTruthy();
        // validate the absence of user dropdown menu
        this.expectByCssToBeAbsent(userDropdownMenu);
    }

};

module.exports = aldrynTestsLibrary;
