var webpack = require("webpack");
var path = require('path');

module.exports = {
    entry: [
        './src/js/jquery_follow.js',
        './src/js/jquery_func.js',
        './src/js/jquery_like.js'
    ],
    mode: 'development',
    output: {
        filename: 'index.js',
        path: __dirname
    },
    plugins: [
        new webpack.ProvidePlugin({
            $: "jquery",
            jQuery: "jquery"
        })
    ]
}