var gulp = require('gulp'),
    path = require('path'),
    concat = require('gulp-concat'),
    browserify = require('browserify'),
    bulkify = require('bulkify'),
    globify = require('require-globify'),
    babelify = require("babelify"),
    less = require('gulp-less'),
    gulpif = require('gulp-if'),
    jshint = require('gulp-jshint'),
    uglify = require('gulp-uglify'),
    source = require('vinyl-source-stream'),
    buffer = require('vinyl-buffer'),
    es    = require('event-stream'),
    gutil = require('gulp-util'),
    minifycss = require('gulp-minify-css'),
    del = require('del'),
    argv = require('yargs').argv;


//
// Path definitions.
// Most setups don't separate vendor scripts from app scripts. But we're going to do it anyway.
// TODO: Cleanup file system so that we can use entire folders.
// TODO: Do this better.
var paths = {
    libraries: [
        'bower_components/jquery/dist/jquery.js',
        'bower_components/bootstrap/js/alert.js',
        'bower_components/bootstrap/js/dropdown.js',
        'bower_components/bootstrap/js/modal.js',
        'bower_components/bootstrap/js/tooltip.js',
        'bower_components/bootstrap/js/popover.js',
        'bower_components/bootstrap/js/tab.js',
        'bower_components/lightbox2/dist/js/lightbox.js',
        'bower_components/waypoints/lib/jquery.waypoints.js',
        'bower_components/Autolinker.js/dist/Autolinker.js',
        'bower_components/remarkable-bootstrap-notify/dist/bootstrap-notify.js',
        'bower_components/imagesloaded/imagesloaded.pkgd.min.js',
        'bower_components/jquery-mousewheel/jquery.mousewheel.js',
        'bower_components/bootstrap-switch/dist/js/bootstrap-switch.js',
        'bower_components/packery/dist/packery.pkgd.js',
        'js/vendor/flatui/radiocheck.js',
        'js/vendor/flatui/fileinput.js',
        'js/vendor/typeahead.js',
        'js/vendor/formvalidation/formValidation.min.js',
        'js/vendor/formvalidation/bootstrap.min.js',
        '../sagebrew/static/js/vendor/spin.min.js',
        '../sagebrew/static/js/vendor/jquery.spin.js',
        '../sagebrew/static/js/vendor/foggy.min.js',
        '../sagebrew/static/js/vendor/jquery.pagedown-bootstrap.combined.min.js',
        '../sagebrew/static/js/vendor/bootstrap-tokenfield.min.js',
        '../sagebrew/static/js/vendor/sortable.min.js',
        '../sagebrew/static/js/uuid.js',
        '../sagebrew/static/js/sbcropic.js',
        '../sagebrew/static/js/sb_utils.js', // These need to updated to support the new JS structure.
                          // Considering them global vendor like scripts for now. to prevent the site from breaking.
        '../sagebrew/static/js/sign_up_btn.js'
    ],
    global_modules: [
        'js/src/sagebrew.js'
    ],
    styles: [
        'styles/**/*.less'
    ],
    fonts: [
        'bower_components/fontawesome/fonts/*',
        'fonts/**'
    ],
    images: [
        'bower_components/lightbox2/dist/images/*',
        'bower_components/croppic/assets/img/*',
        '../sagebrew/static/images/*.png',
        '../sagebrew/static/images/*.gif',
        '../sagebrew/static/images/*.jpg',
        '../sagebrew/static/media/*'

    ]
};

var production = argv.env === 'production';

//
// TODO: Make this work. Clean BAF again.
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
// App Scripts - Lint
gulp.task('scripts:lint', function () {
    return gulp.src(['js/src/**'])
            .pipe(gulpif(!production, jshint('.jshintrc')))
            .pipe(gulpif(!production, jshint.reporter('jshint-stylish')))
            .on('error', gutil.log);
});

//
// App Scripts - Global
gulp.task('scripts:global', function () {
    var tasks = paths.global_modules.map(function(entry) {

        var source_name = path.basename(entry);
        var module_name = path.basename(entry, '.js');
        var debug = true;
        if (production) {
            debug = false;
        }
        var bundler =  browserify({
            entries: [__dirname + "/" + entry],
            basedir: __dirname,
            debug: debug
            //transform: [bulkify, babelify]
        });

        bundler.transform(babelify);
        bundler.transform(globify);

        bundler.require(__dirname + "/" + entry, { expose: module_name});

        return bundler
            .bundle()
            .on('error', function(err){
                console.log(err.message);
                this.emit("end");
            })
            .pipe(source(source_name))
            .pipe(buffer())
            .pipe(gulpif(production, uglify())) // now gulp-uglify works
            .on('error', gutil.log)
            .pipe(gulp.dest('../sagebrew/static/dist/js/'));
        });

    // create a merged stream
    return es.merge.apply(null, tasks);
});

//
// JS - Vendor aka catchall.
gulp.task('scripts:vendor', function () {
    return gulp.src(paths.libraries)
        .pipe(concat('vendor.js'))
        .pipe(gulpif(production, uglify()))
        .on('error', gutil.log)
        .pipe(gulp.dest('../sagebrew/static/dist/js'));
});

//
// JS
gulp.task('scripts', ['scripts:lint', 'scripts:global', 'scripts:vendor']);

//
// Styles
gulp.task('styles', function () {
    return gulp.src(['styles/styles.less'])
        .pipe(less())
        .on('error', gutil.log)
        .pipe(minifycss())
        .on('error', gutil.log)
        .pipe(gulp.dest('../sagebrew/static/dist/css/'));
});

//
// Fonts
gulp.task('fonts', function() {
    return gulp.src(paths.fonts)
            .on('error', gutil.log)
            .pipe(gulp.dest('../sagebrew/static/dist/fonts/'));
});

//
// Hotfix for lightbox images.
// TODO: Fix.
gulp.task('images:hotfix', function() {
    return gulp.src(['css/vendor/img/**'])
            .on('error', gutil.log)
           .pipe(gulp.dest('../sagebrew/static/dist/css/vendor/img/'));
});

//
// Images
gulp.task('images', ['images:hotfix'], function() {
    return gulp.src(paths.images)
            .on('error', gutil.log)
            .pipe(gulp.dest('../sagebrew/static/dist/images/'));
});


//
// Default task.
gulp.task('watch', function () {
    'use strict';
    gulp.watch(paths.styles, ['styles']);
    gulp.watch(['js/src/**'], ['scripts:lint', 'scripts:global']);

});

//
// Build
gulp.task('build', ['scripts', 'styles', 'images', 'fonts']);

//
// Default task.
gulp.task('default', ['watch', 'scripts', 'styles', 'images', 'fonts']);