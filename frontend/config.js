var webpack = require("webpack");
var path = require('path');
var MiniCssExtractPlugin = require('mini-css-extract-plugin');

config_js = {
    entry: [
        './src/js/jquery_follow.js',
        './src/js/jquery_func.js',
        './src/js/jquery_like.js'
    ],
    mode: 'development',
    output: {
        filename: 'index.js',
        path: path.resolve(__dirname, '../djangogramm/static/djangogramm/js/')
    },
    plugins: [
        new webpack.ProvidePlugin({
            $: "jquery",
            jQuery: "jquery"
        })
    ]
}

config_css = {
  entry: './src/css/main_css.js',
  mode: 'development',
  output: {
        filename: 'main.css',
        path: path.resolve(__dirname, '../djangogramm/static/djangogramm/css/')
    },
  plugins: [new MiniCssExtractPlugin({
    filename: 'index.css'
  })],
  module: {
      rules: [
          {
            test: /\.css$/i,
            use: [MiniCssExtractPlugin.loader, "css-loader"],
          },
      ],
  },
}

module.exports = [config_js, config_css]
