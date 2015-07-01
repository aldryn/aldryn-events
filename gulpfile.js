/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

'use strict';

// #####################################################################################################################
// #IMPORTS#
var gulp = require('gulp');
var gutil = require('gulp-util');
var karma = require('karma').server;
var protractor = require('gulp-protractor').protractor;
// Download and update the selenium driver
var webdriverUpdate = require('gulp-protractor').webdriver_update;

// #####################################################################################################################
// #SETTINGS#
var PROJECT_ROOT = '.';
var PROJECT_PATH = {
    'tests': PROJECT_ROOT + '/tests'
};

// #########################################################
// #TESTS#
gulp.task('tests', ['tests:unit', 'tests:integration']);
gulp.task('tests:unit', function (done) {
    // run javascript tests
    karma.start({
        'configFile': __dirname + '/tests/karma.conf.js',
        'singleRun': true
    }, done);
});

gulp.task('tests:webdriver', webdriverUpdate);
gulp.task('tests:integration', ['tests:webdriver'], function () {
    return gulp.src([PROJECT_PATH.tests + '/integration/*.js'])
        .pipe(protractor({
            configFile: PROJECT_PATH.tests + '/protractor.conf.js',
            args: []
        }))
        .on('error', function (error) {
            gutil.log(gutil.colors.red('Error (' + error.plugin + '): ' + error.message));
        });
});

gulp.task('karma', function () {
    // run javascript tests
    karma.start({
        'configFile': __dirname + '/tests/karma.conf.js'
    });
});

// #####################################################################################################################
// #COMMANDS#
gulp.task('default', ['tests']);
