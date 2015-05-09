var gulp = require('gulp');
var concat = require('gulp-concat');
var less = require('gulp-less');
var minifyCSS = require('gulp-minify-css');
var embedlr = require('gulp-embedlr');

gulp.task('scripts', function() {
    gulp.src(['js/**/*.js'])
        .pipe(concat('dest.js'))
        .pipe(gulp.dest('dist/build'))
})

gulp.task('styles', function() {
    gulp.src(['less/styles.less'])
        .pipe(less())
        .pipe(minifyCSS())
        .pipe(gulp.dest('dist/build'))
})

gulp.task('default', function() {
    gulp.run('styles');

    gulp.watch('less/**', function(event) {
        gulp.run('styles');
    })

})