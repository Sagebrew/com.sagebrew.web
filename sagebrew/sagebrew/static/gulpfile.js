//
// Load various glup plugins.
var gulp = require('gulp'),
    concat = require('gulp-concat'),
    less = require('gulp-less'),
    jshint = require('gulp-jshint'),
    uglify = require('gulp-uglify'),
    minifycss = require('gulp-minify-css'),
    embedlr = require('gulp-embedlr'),
    clean = require('gulp-clean'),
    refresh = require('gulp-livereload'),
    lr = require('tiny-lr'),
    server = lr(),
    notify = require('gulp-notify');

//
// Path definitions.
// Most setups don't separate vendor scripts from app scripts. But we're going to do it anyway.
// TODO: Cleanup file system so that we can use entire folders.
var paths = {
    vendor_scripts: [
        'js/vendor/jquery-2.1.4.min.js',
        'js/vendor/bootstrap.min.js',
        'js/vendor/bootstrap-notify.min.js',
        'js/vendor/formValidation.min.js',
        'js/vendor/framework/bootstrap.min.js', // I think this is something to do with formvalidor and not actually the bootstrap js.
        'js/vendor/imagesloaded.pkgd.min.js',
        'js/vendor/packery.pkgd.min.js',
        'js/vendor/spin.min.js',
        'js/vendor/jquery.spin.js',
        'js/vendor/foggy.min.js',
        'js/vendor/Autolinker.min.js'
    ],
    scripts: [
        'js/sb_utils.js',
        'js/sign_up_btn.js'
    ],
    styles: [
        'less/**'
    ],
    fonts: [
        'css/vendor/font-awesome-4.3.0/fonts/*',
        'fonts/*'
    ],
    images: [
        'css/vendor/img/**',
        'images/**',
        '!images/congress',
        'media/**'
    ]
};

//
// JS
gulp.task('scripts', function () {
    'use strict';
    gulp.src(paths.vendor_scripts)
        .pipe(concat('vendor.js'))
        .pipe(gulp.dest('dist/build'))
        .pipe(refresh(server));

    gulp.src(paths.scripts)
        .pipe(jshint('.jshintrc'))
        .pipe(jshint.reporter('jshint-stylish'))
        .pipe(concat('sagebrew.js'))
        .pipe(gulp.dest('dist/build'))
        .pipe(refresh(server));
});

//
// Styles
gulp.task('styles', function () {
    gulp.src(['less/styles.less'])
        .pipe(less())
        .pipe(minifycss())
        .pipe(gulp.dest('dist/build'))
        .pipe(refresh(server));
});

//
// LR Server
// TODO: make this work.
gulp.task('lr-server', function() {
    server.listen(35729, function(err) {
        if(err) return console.log(err);
    });
});

//
// Fonts
gulp.task('fonts', function() {
    gulp.src(paths.fonts)
            .pipe(gulp.dest('dist/fonts/'));
});

//
// Images
gulp.task('images', function() {
    gulp.src(paths.images)
            .pipe(gulp.dest('dist/imgs/'));

    //Bad fix for lightbox.
    //TODO: Stop This...
    gulp.src(['css/vendor/img/**'])
            .pipe(gulp.dest('dist/css/vendor/img/'));
});

//
// Clean
// TODO: Fix this, it throws an error.
gulp.task('clean', function () {
    gulp.src(['dist/build', 'dist/fonts', 'dist/imgs'], { read: false })
        .pipe(clean());
});

//
// Default task.
gulp.task('default', function () {
    'use strict';

    var client = ['lr-server', 'styles', 'scripts', 'fonts', 'images'];
    gulp.run(client);

    //TODO: Only rebuild styles when styles are edited, only rebuild scripts when scripts are edited.
    gulp.watch(paths.styles, client);
    gulp.watch(paths.scripts, client);

});