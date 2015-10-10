var gulp = require('gulp');
var concat = require('gulp-concat');
var less = require('gulp-less');
var jshint = require('gulp-jshint');
var uglify = require('gulp-uglify');
var source = require('vinyl-source-stream');
var buffer = require('vinyl-buffer');
var sourcemaps = require('gulp-sourcemaps');
var gutil = require('gulp-util');
var minifycss = require('gulp-minify-css');
var embedlr = require('gulp-embedlr');
var del = require('del');
var refresh = require('gulp-livereload');
var lr = require('tiny-lr');
var server = lr();
var notify = require('gulp-notify');

//
// Path definitions.
// Most setups don't separate vendor scripts from app scripts. But we're going to do it anyway.
// TODO: Cleanup file system so that we can use entire folders.
// TOOO: Merge scripts, scripts-anon, scripts-auth into one.
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
        'less/**/*.less'
    ],
    fonts: [
        'css/vendor/font-awesome-4.3.0/fonts/*',
        'fonts/*'
    ],
    images: [
        'css/vendor/img/**',
        'images/*.png',
        'images/*.gif',
        'images/*.jpg',
        '!images/congress',
        'media/**'
    ]
};


//
// Clean
gulp.task('clean', function() {
  return del(['dist']);
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
// JS
gulp.task('scripts:app', ['clean'], function () {
    return gulp.src(paths.scripts)
        .pipe(jshint('.jshintrc'))
        .pipe(jshint.reporter('jshint-stylish'))
        .pipe(concat('sagebrew.js'))
        .pipe(gulp.dest('dist/js'))
        .pipe(refresh(server));

});

//
// JS
gulp.task('scripts:vendor', ['clean'], function () {
    return gulp.src(paths.vendor_scripts)
        .pipe(concat('vendor.js'))
        .pipe(gulp.dest('dist/js'))
        .pipe(refresh(server));
});

//
// JS
gulp.task('scripts', ['scripts:vendor', 'scripts:app']);

//
// Styles
gulp.task('styles', ['clean'], function () {
    return gulp.src(['less/styles.less'])
        .pipe(less())
        .pipe(minifycss())
        .pipe(gulp.dest('dist/css'))
        .pipe(refresh(server));
});


//
// Fonts
gulp.task('fonts', ['clean'], function() {
    return gulp.src(paths.fonts)
            .pipe(gulp.dest('dist/fonts/'));
});


//
// Hotfix for lightbox images.
// TODO: Fix.
gulp.task('images:hotfix', ['clean'], function() {
    return gulp.src(['css/vendor/img/**'])
           .pipe(gulp.dest('dist/css/vendor/img/'));
});

//
// Images
gulp.task('images', ['clean', 'images:hotfix'], function() {
    return gulp.src(paths.images)
            .pipe(gulp.dest('dist/imgs/'));
});

//
// Default task.
gulp.task('watch', function () {
    'use strict';

    gulp.watch(paths.styles, ['styles']);
    gulp.watch(paths.scripts, ['scripts']);

});

//
// Default task.
gulp.task('default', ['watch', 'scripts', 'styles', 'images', 'fonts']);