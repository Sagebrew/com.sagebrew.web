var gulp = require('gulp'),
    path = require('path'),
    concat = require('gulp-concat'),
    browserify = require('browserify'),
    globify = require('require-globify'),
    hbsfy = require('hbsfy'),
    babelify = require("babelify"),
    less = require('gulp-less'),
    wrap = require('gulp-wrap'),
    declare = require('gulp-declare'),
    gulpif = require('gulp-if'),
    jshint = require('gulp-jshint'),
    uglify = require('gulp-uglify'),
    source = require('vinyl-source-stream'),
    buffer = require('vinyl-buffer'),
    es    = require('event-stream'),
    gutil = require('gulp-util'),
    minifycss = require('gulp-minify-css'),
    argv = require('yargs').argv;


/**
 * Config 
 */
var config = {
    libraries: [
        'bower_components/jquery/dist/jquery.js',
        'bower_components/bootstrap/js/alert.js',
        'bower_components/bootstrap/js/dropdown.js',
        'bower_components/bootstrap/js/modal.js',
        'bower_components/bootstrap/js/tooltip.js',
        'bower_components/bootstrap/js/popover.js',
        'bower_components/bootstrap/js/collapse.js',
        'bower_components/bootstrap/js/tab.js',
        'bower_components/lightbox2/dist/js/lightbox.js',
        'bower_components/jquery.payment/lib/jquery.payment.js',
        'bower_components/waypoints/lib/jquery.waypoints.js',
        'bower_components/Autolinker.js/dist/Autolinker.js',
        'bower_components/remarkable-bootstrap-notify/dist/bootstrap-notify.js',
        'bower_components/imagesloaded/imagesloaded.pkgd.min.js',
        'bower_components/jquery-mousewheel/jquery.mousewheel.js',
        'bower_components/bootstrap-switch/dist/js/bootstrap-switch.js',
        'bower_components/packery/dist/packery.pkgd.js',
        'bower_components/medium-editor-insert-plugin/js/medium-editor-insert-plugin.min.js',
        'node_modules/bootstrap-tokenfield/dist/bootstrap-tokenfield.min.js', // TODO Remove this after transitioning registration and tag input to new format and use require
        'js/vendor/flatui/radiocheck.js',
        'js/vendor/flatui/fileinput.js',
        'bower_components/typeahead.js/dist/typeahead.bundle.min.js',
        'js/vendor/liveaddress.min.js',
        'js/vendor/formvalidation/formValidation.min.js',
        'js/vendor/formvalidation/bootstrap.min.js',
        'js/vendor/card.js',
        'js/vendor/spin.min.js',
        'js/vendor/jquery.spin.js',
        'js/vendor/foggy.min.js',
        'js/vendor/jquery.pagedown-bootstrap.combined.min.js',
        'js/vendor/sortable.min.js',


        /**
         *  Various "legacy" Js Files still in use somewhere.
         *
         *  sbcroppic: This is needed rather than bower because we've made custom mods
         *  to the file to resolve some issues and the package appears to
         *  be primarily unmaintained now.
         */
        'js/legacy/uuid.js',
        'js/legacy/sbcropic.js',
        'js/legacy/sb_utils.js',
        'js/legacy/sign_up_btn.js'
    ],
    global_modules: [
        'js/src/sagebrew.js'
    ],
    styles: [
        'styles/**/*.less'
    ],
    fonts: [
        'bower_components/fontawesome/fonts/*',
        'assets/fonts/**'
    ],
    videos: [
        'assets/videos/**'
    ],
    images: [
        'bower_components/lightbox2/dist/images/*',
        'bower_components/croppic/assets/img/*',
        'assets/images/**'
    ],
    build_dir: "build/"
};

var production = argv.env === 'production';

//
// App Scripts - Lint
gulp.task('scripts:lint', function () {
    return gulp.src(['js/src/**/*.js'])
            .pipe(gulpif(!production, jshint('.jshintrc')))
            .pipe(gulpif(!production, jshint.reporter('jshint-stylish')))
            .on('error', gutil.log);
});
//
// App Scripts - Global
gulp.task('scripts:global', function () {
    var tasks = config.global_modules.map(function(entry) {

        var source_name = path.basename(entry);
        var module_name = path.basename(entry, '.js');
        var debug = true;
        if (production) {
            debug = false;
        }
        var bundler =  browserify({
            entries: [__dirname + "/" + entry],
            basedir: __dirname,
            debug: debug,
            paths: [
                './node_modules',
                './js/src/components'
            ]
        });


        bundler.transform(babelify, {presets: ["es2015", "react"]});
        bundler.transform(hbsfy,  { traverse: true });
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
            .pipe(gulp.dest(config.build_dir+'js/'));
        });

    // create a merged stream
    return es.merge.apply(null, tasks);
});

//
// JS - Vendor aka catchall.
gulp.task('scripts:vendor', function () {
    return gulp.src(config.libraries)
        .pipe(concat('vendor.js'))
        .pipe(gulpif(production, uglify()))
        .on('error', gutil.log)
        .pipe(gulp.dest(config.build_dir+'js/'));
});



//
// Fonts
gulp.task('assets:fonts', function() {
    return gulp.src(config.fonts)
            .on('error', gutil.log)
            .pipe(gulp.dest(config.build_dir+'fonts/'));
});

//
// videos
gulp.task('assets:videos', function() {
    return gulp.src(config.videos)
            .on('error', gutil.log)
            .pipe(gulp.dest(config.build_dir+'videos/'));
});

//
// Hotfix for lightbox images.
// TODO: Fix.
gulp.task('assets:imageshotfix', function() {
    return gulp.src(['css/vendor/img/**'])
            .on('error', gutil.log)
           .pipe(gulp.dest(config.build_dir+'css/vendor/img/'));
});

//
// Images
gulp.task('assets:images',  function() {
    return gulp.src(config.images)
            .on('error', gutil.log)
            .pipe(gulp.dest(config.build_dir+'images/'));
});



//
// Styles
gulp.task('styles', function () {
    return gulp.src(['styles/styles.less'])
        .pipe(less({
            paths: [
                path.join(__dirname, 'styles'),
                path.join(__dirname, 'bower_components')
            ]
        }))
        .on('error', gutil.log)
        .pipe(minifycss())
        .on('error', gutil.log)
        .pipe(gulp.dest(config.build_dir+'css/'));
});

//
// JS
gulp.task('scripts', [
    'scripts:lint',
    'scripts:global',
    'scripts:vendor']);

//
// Assets
gulp.task('assets', [
    'assets:fonts',
    'assets:videos',
    'assets:imageshotfix',
    'assets:images']);

//
// Default task.
gulp.task('watch', function () {
    'use strict';
    gulp.watch(config.styles, ['styles']);
    gulp.watch(['./js/src/**'], ['scripts:lint', 'scripts:global']);

});

//
// Build
gulp.task('build', ['scripts', 'styles', 'assets']);

//
// Default task.
gulp.task('default', ['watch', 'scripts', 'styles', 'assets']);