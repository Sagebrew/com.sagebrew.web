var gulp = require('gulp'),
    path = require('path'),
    concat = require('gulp-concat'),
    browserify = require('browserify'),
    bulkify = require('bulkify'),
    globify = require('require-globify'),
    babelify = require("babelify"),
    less = require('gulp-less'),
    imagemin = require('gulp-imagemin'),
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
        'bower_components/jquery/dist/jquery.js',
        'bower_components/bootstrap/dist/js/bootstrap.js',
        'bower_components/lightbox2/dist/js/lightbox.js',
        '../sagebrew/static/js/vendor/bootstrap-notify.min.js',
        '../sagebrew/static/js/vendor/formValidation.min.js',
        '../sagebrew/static/js/vendor/framework/bootstrap.min.js', // I think this is something to do with validator and not actually the bootstrap js.
        '../sagebrew/static/js/vendor/imagesloaded.pkgd.min.js',
        '../sagebrew/static/js/vendor/packery.pkgd.min.js',
        '../sagebrew/static/js/vendor/spin.min.js',
        '../sagebrew/static/js/vendor/jquery.spin.js',
        '../sagebrew/static/js/vendor/foggy.min.js',
        '../sagebrew/static/js/vendor/Autolinker.min.js',
        '../sagebrew/static/js/vendor/croppic.min.js',
        '../sagebrew/static/js/vendor/jquery.mousewheel.min.js',
        '../sagebrew/static/js/vendor/jquery.pagedown-bootstrap.combined.min.js',
        '../sagebrew/static/js/uuid.js',
        '../sagebrew/static/js/sb_utils.js', // These need to updated to support the new JS structure.
                          // Considering them global vendor like scripts for now. to prevent the site from breaking.
        '../sagebrew/static/js/sign_up_btn.js'
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
        'bower_components/fontawesome/fonts/*',
        'fonts/**'
    ],
    images: [
        'styles/contrib/misc/css/vendor/img/**',
        '../sagebrew/static/images/*.png',
        '../sagebrew/static/images/*.gif',
        '../sagebrew/static/images/*.jpg',
        '!../sagebrew/static/images/congress',
        '../sagebrew/static/media/**',
        'bower_components/lightbox2/dist/images/*'
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
            debug: true
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
            // rename them to have "bundle as postfix"
            //.pipe(rename({
            //    extname: '.bundle.js'
            //}))
            .pipe(jshint('.jshintrc'))
            .pipe(jshint.reporter('jshint-stylish'))
            .on('error', gutil.log)
            .pipe(gulp.dest('../sagebrew/static/dist/js/'));
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
            .pipe(gulp.dest('../sagebrew/static/dist/js/'));
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
            .pipe(gulp.dest('../sagebrew/static/dist/js/'));
        });

    // create a merged stream
    return es.merge.apply(null, tasks);


});

//
// JS
gulp.task('scripts:vendor', function () {
    return gulp.src(paths.libraries)
        .pipe(concat('vendor.js'))
        //.pipe(uglify())
        .pipe(gulp.dest('../sagebrew/static/dist/js'))
        .on('error', gutil.log)
        .pipe(refresh(server));

});

//
// JS
gulp.task('scripts', ['scripts:global', 'scripts:user', 'scripts:section', 'scripts:vendor']);

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
            .pipe(gulp.dest('../sagebrew/static/dist/fonts/'));
});

//
// Hotfix for lightbox images.
// TODO: Fix.
gulp.task('images:hotfix', function() {
    return gulp.src(['css/vendor/img/**'])
           .pipe(gulp.dest('../sagebrew/static/dist/css/vendor/img/'));
});

//
// Images
gulp.task('images', ['images:hotfix'], function() {
    return gulp.src(paths.images)
            .pipe(imagemin({
                progressive: true,
                svgoPlugins: [{removeViewBox: false}]
            }))
            .pipe(gulp.dest('../sagebrew/static/dist/images/'));
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