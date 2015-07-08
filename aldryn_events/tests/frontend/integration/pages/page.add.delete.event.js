/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

// ACCEPTANCE TEST
// #############################################################################
'use strict';
/* global by, element */
/* jshint browser: true */
/* jshint shadow: true */

/**
 * This file uses the Page Object pattern to define a test.
 **/

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
};

module.exports = aldrynEventsPage;
