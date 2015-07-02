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
var jshint = require('gulp-jshint');
var jscs = require('gulp-jscs');
// Download and update the selenium driver
var webdriverUpdate = require('gulp-protractor').webdriver_update;

// #####################################################################################################################
// #SETTINGS#
var PROJECT_ROOT = '.';
var PROJECT_PATH = {
    'js': PROJECT_ROOT + '/aldryn_events/boilerplates/bootstrap3/static/js/',
    'tests': PROJECT_ROOT + '/fe_tests'
};

var PROJECT_PATTERNS = {
    'jslint': [
        PROJECT_PATH.js + '/addons/*.js',
        PROJECT_ROOT + '/fe_tests/*.js',
        PROJECT_ROOT + '/fe_tests/unit/*.js',
        PROJECT_ROOT + '/fe_tests/integration/*.js',
        PROJECT_ROOT + '/gulpfile.js'
    ]
};

// #####################################################################################################################
// #LINTING#
gulp.task('jslint', function () {
    gulp.src(PROJECT_PATTERNS.jslint)
        .pipe(jshint())
        .pipe(jscs())
        .on('error', function (error) {
            gutil.log('\n' + error.message);
        })
        .pipe(jshint.reporter('jshint-stylish'));
});

// #########################################################
// #TESTS#
gulp.task('tests', ['tests:unit', 'tests:lint']);
gulp.task('tests:lint', ['jslint']);
gulp.task('tests:unit', function (done) {
    // run javascript tests
    karma.start({
        'configFile': __dirname + '/fe_tests/karma.conf.js',
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
        'configFile': __dirname + '/fe_tests/karma.conf.js'
    });
});

// #####################################################################################################################
// #COMMANDS#
gulp.task('default', ['jslint']);
