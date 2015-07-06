/*!
 * @author:    Divio AG
 * @copyright: http://www.divio.ch
 */

'use strict';

// #############################################################################
// IMPORTS
var gulp = require('gulp');
var gutil = require('gulp-util');
var karma = require('karma').server;
var protractor = require('gulp-protractor').protractor;
var jshint = require('gulp-jshint');
var jscs = require('gulp-jscs');
var webdriverUpdate = require('gulp-protractor').webdriver_update;

// #############################################################################
// SETTINGS
var PROJECT_ROOT = __dirname;
var PROJECT_PATH = {
    'js': PROJECT_ROOT + '/aldryn_events/boilerplates/bootstrap3/static/js/',
    'tests': PROJECT_ROOT + '/aldryn_events/tests/frontend'
};

var PROJECT_PATTERNS = {
    'lint': [
        PROJECT_PATH.js + '/addons/*.js',
        PROJECT_PATH.tests + '/*.js',
        PROJECT_PATH.tests + '/unit/*.js',
        PROJECT_PATH.tests + '/integration/*.js',
        PROJECT_ROOT + '/gulpfile.js'
    ]
};

// #############################################################################
// LINTING
gulp.task('lint', function () {
    gulp.src(PROJECT_PATTERNS.lint)
        .pipe(jshint())
        .pipe(jscs())
        .on('error', function (error) {
            gutil.log('\n' + error.message);
        })
        .pipe(jshint.reporter('jshint-stylish'))
        .pipe(jshint.reporter('fail'));
});

// #########################################################
// TESTS
gulp.task('tests', ['tests:unit', 'tests:lint']);
gulp.task('tests:lint', ['lint']);
gulp.task('tests:unit', function (done) {
    // run javascript tests
    karma.start({
        configFile: PROJECT_PATH.tests + '/karma.conf.js',
        singleRun: true
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
            gutil.log(gutil.colors.red(
                'Error (' + error.plugin + '): ' + error.message
            ));
        });
});

gulp.task('tests:watch', function () {
    // run javascript tests
    karma.start({
        configFile: PROJECT_PATH.tests + '/karma.conf.js'
    });
});

// #############################################################################
// COMMANDS
gulp.task('default', ['lint']);
