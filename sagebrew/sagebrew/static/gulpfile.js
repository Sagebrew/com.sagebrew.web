var gulp = require('gulp'),
    path = require('path'),
    concat = require('gulp-concat'),
    browserify = require('browserify'),
    babelify = require("babelify"),
    less = require('gulp-less'),
    jshint = require('gulp-jshint'),
    uglify = require('gulp-uglify'),
    source = require('vinyl-source-stream'),
    buffer = require('vinyl-buffer'),
    sourcemaps = require('gulp-sourcemaps'),
    rename     = require('gulp-rename'),
    es    = require('event-stream'),
    gutil = require('gulp-util'),
    minifycss = require('gulp-minify-css'),
    del = require('del'),
    refresh = require('gulp-livereload'),
    lr = require('tiny-lr'),
    server = lr();


//
// Path definitions.
// Most setups don't separate vendor scripts from app scripts. But we're going to do it anyway.
// TODO: Cleanup file system so that we can use entire folders.
// TODO: Do this better.
var paths = {
    libraries: [
        'js/vendor/jquery-2.1.4.min.js',
        'js/vendor/bootstrap.min.js',
        'js/vendor/bootstrap-notify.min.js',
        'js/vendor/formValidation.min.js',
        'js/vendor/framework/bootstrap.min.js', // I think this is something to do with validator and not actually the bootstrap js.
        'js/vendor/imagesloaded.pkgd.min.js',
        'js/vendor/packery.pkgd.min.js',
        'js/vendor/spin.min.js',
        'js/vendor/jquery.spin.js',
        'js/vendor/foggy.min.js',
        'js/vendor/Autolinker.min.js',
        'js/vendor/croppic.min.js',
        'js/vendor/lightbox.min.js',
        'js/vendor/jquery.mousewheel.min.js',
        'js/vendor/jdquery.pagedown-bootstrap.combined.min.js',
        'js/uuid.js',
        'js/sb_utils.js', // These need to updated to support the new JS structure.
                          // Considering them global vendor like scripts for now. to prevent the site from breaking.
        'js/sign_up_btn.js'
    ],
    global_modules: [
        'js/src/sagebrew.js'
    ],
    user_modules: [
        'js/src/user-anoned.js',
        'js/src/user-authed.js'
    ],
    section_modules: [
        'js/src/section-profile.js'
    ],
    styles: [
        'styles/**/*.less'
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
// Clean BAF again.
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
// App Scripts - Global
gulp.task('scripts:global', function () {
    var tasks = paths.global_modules.map(function(entry) {

        var source_name = path.basename(entry);
        var module_name = path.basename(entry, '.js');

        var bundler =  browserify({
            entries: [__dirname + "/" + entry],
            basedir: __dirname,
            debug: true,
            transform: [babelify]
        });

        bundler.require(__dirname + "/" + entry, { expose: module_name});

        return bundler
            .bundle()
            .on('error', function(err){
                console.log(err.message);
                this.emit("end");
            })
            .pipe(source(source_name))
            // rename them to have "bundle as postfix"
            //.pipe(rename({
            //    extname: '.bundle.js'
            //}))
            .pipe(jshint('.jshintrc'))
            .pipe(jshint.reporter('jshint-stylish'))
            .on('error', gutil.log)
            .pipe(gulp.dest('dist/js/'));
        });

    // create a merged stream
    return es.merge.apply(null, tasks);
});

//
// App Scripts - User
gulp.task('scripts:user', function () {
    var tasks = paths.user_modules.map(function(entry) {

        var source_name = path.basename(entry);
        var module_name = path.basename(entry, '.js');

        var bundler =  browserify({
            entries: [__dirname + "/" + entry],
            basedir: __dirname,
            debug: true,
            transform: [babelify]
        });

        bundler.external('sagebrew');
        bundler.require(__dirname + "/" + entry, { expose: module_name});

        return bundler
            .bundle()
            .on('error', function(err){
                console.log(err.message);
                this.emit("end");
            })
            .pipe(source(source_name))
            // rename them to have "bundle as postfix"
            //.pipe(rename({
            //    extname: '.bundle.js'
            //}))
            .pipe(jshint('.jshintrc'))
            .pipe(jshint.reporter('jshint-stylish'))
            .on('error', gutil.log)
            .pipe(gulp.dest('dist/js/'));
        });

    // create a merged stream
    return es.merge.apply(null, tasks);
});

//
// App Scripts - Sections
gulp.task('scripts:section', function () {

    var tasks = paths.section_modules.map(function(entry) {
        var source_name = path.basename(entry);
        var module_name = path.basename(entry, '.js');

        var bundler =  browserify({
            entries: [__dirname + "/" + entry],
            basedir: __dirname,
            debug: true,
            transform: [babelify]
        });

        //TODO: -- Make this fancy.
        bundler.external('sagebrew');
        bundler.external('user-anoned');
        bundler.external('user-authed');

        return bundler
            .bundle()
            .on('error', function(err){
                  console.log(err.message);
                  this.emit("end");
            })
            .pipe(source(source_name))
            // rename them to have "bundle as postfix"
            //.pipe(rename({
            //    extname: '.bundle.js'
            //}))
            .pipe(jshint('.jshintrc'))
            .pipe(jshint.reporter('jshint-stylish'))
            .on('error', gutil.log)
            .pipe(gulp.dest('dist/js/'));
        });

    // create a merged stream
    return es.merge.apply(null, tasks);


});

//
// JS
gulp.task('scripts:vendor', function () {
    return gulp.src(paths.libraries)
        .pipe(concat('vendor.js'))
        .pipe(gulp.dest('dist/js'))
        .pipe(refresh(server));

});

//
// JS
gulp.task('scripts', ['scripts:global', 'scripts:user', 'scripts:section', 'scripts:vendor']);

//
// Styles
gulp.task('styles', function () {
    return gulp.src(['less/styles.less'])
        .pipe(less())
        .pipe(minifycss())
        .pipe(gulp.dest('dist/css'))
        .pipe(refresh(server));
});

//
// Fonts
gulp.task('fonts', function() {
    return gulp.src(paths.fonts)
            .pipe(gulp.dest('dist/fonts/'));
});

//
// Hotfix for lightbox images.
// TODO: Fix.
gulp.task('images:hotfix', function() {
    return gulp.src(['css/vendor/img/**'])
           .pipe(gulp.dest('dist/css/vendor/img/'));
});

//
// Images
gulp.task('images', ['images:hotfix'], function() {
    return gulp.src(paths.images)
            .pipe(gulp.dest('dist/imgs/'));
});

//
// Default task.
gulp.task('watch', function () {
    'use strict';

    gulp.watch(paths.styles, ['styles']);
    gulp.watch(['js/src/**'], ['scripts']);

});

//
// Default task.
gulp.task('default', ['watch', 'scripts', 'styles', 'images', 'fonts']);