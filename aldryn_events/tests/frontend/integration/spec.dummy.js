/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

'use strict';
/* global describe, it, expect, browser */

// #############################################################################
// INTEGRATION TEST
describe('Django CMS website', function () {
    it('should have a title', function () {
        browser.get('http://127.0.0.1:8000');

        expect(browser.getTitle()).toContain('django CMS');
    });
});
