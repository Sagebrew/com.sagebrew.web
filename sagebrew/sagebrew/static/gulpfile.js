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
// TODO: Merge scripts, scripts-anon, scripts-auth into one.
var paths = {
    libraries: [
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
        'js/vendor/Autolinker.min.js',
        'js/vendor/croppic.min.js',
        'js/vendor/lightbox.min.js',
        'js/vendor/jquery.mousewheel.min.js',
        'js/vendor/jquery.pagedown-bootstrap.combined.min.js',
        'js/uuid.js'
    ],
    core_modules: [
        'js/src/sagebrew.js'
    ],
    modules: [
        'js/src/profile.js'
        //'js/modules/sagebrew/auth.js'
        //'js/sb_utils.js',
        //'js/sign_up_btn.js'
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
// JS
gulp.task('scripts:appcore', function () {
    var tasks = paths.core_modules.map(function(entry) {

        var source_name = path.basename(entry);
        var module_name = path.basename(entry, '.js');

        var bundler =  browserify({
            entries: [__dirname + "/" + entry],
            basedir: __dirname,
            debug: true,
            transform: [babelify]
        });

        return bundler
            .require(__dirname + "/" + entry, { expose: module_name})
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

    /*
    var b = browserify({
        entries: paths.scripts,
        debug: true,
        // defining transforms here will avoid crashing your stream
        transform: [babelify]
    });



    b.add(require.resolve('babel/polyfill'));

    return b.bundle()
        .pipe(source('sagebrew.js'))
        .pipe(buffer())
        .pipe(sourcemaps.init({loadMaps: true}))
            // Add transformation tasks to the pipeline here.
            //.pipe(uglify())
             .pipe(jshint('.jshintrc'))
             .pipe(jshint.reporter('jshint-stylish'))
            .on('error', gutil.log)
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest('dist/js/'));

*/

/*
    return gulp.src(paths.scripts)
        .pipe(sourcemaps.init())
        .pipe(babel())
        .pipe(jshint('.jshintrc'))
        .pipe(jshint.reporter('jshint-stylish'))
        .pipe(concat('sagebrew.js'))
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest('dist/js'))
        .pipe(refresh(server));
        */

});


//
// JS
gulp.task('scripts:appmodules', function () {

    var tasks = paths.modules.map(function(entry) {
        var source_name = path.basename(entry);
        return browserify({ entries: [entry], debug: true, transform: [babelify]})
            .external('sagebrew')
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
    /*
    var files = [];

    for (var i = 0; i < paths.libraries.length; i++) {

        files.push(paths.libraries[i].file);
    }

    console.log(files);

    var b = browserify({
        entries: files,
        debug: true,
        // defining transforms here will avoid crashing your stream
        transform: [babelify]
    });

    for (var j = 0; j < paths.libraries.length; j++) {
        if (paths.libraries[j].external) {
            b.require(paths.libraries[j].file, {external: paths.libraries[j].external});
        } else {
            b.require(paths.libraries[j].file);
        }

    }


    b.add(require.resolve('babel/polyfill'));
    return b.bundle()
        .pipe(source('vendor.js'))
        .pipe(buffer())
            // Add transformation tasks to the pipeline here.
            //.pipe(uglify())
            .on('error', gutil.log)
        .pipe(gulp.dest('dist/js/'));
    */

    return gulp.src(paths.libraries)
        .pipe(concat('vendor.js'))
        .pipe(gulp.dest('dist/js'))
        .pipe(refresh(server));

});

//
// JS
gulp.task('scripts', ['scripts:appcore', 'scripts:appmodules', 'scripts:vendor']);

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