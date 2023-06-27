const { series, src, dest } = require('gulp');

function sortable() {
    const files = [
        'node_modules/sortablejs/Sortable.min.js',
    ]
    return src(files).pipe(dest('mptt2/static/mptt2'))
}

exports.default = series(sortable)