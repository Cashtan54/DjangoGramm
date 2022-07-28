const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');


module.exports = {
  entry: './src/css/main_css.js',
  mode: 'development',
  output: {
    filename: 'index.css',
    path: __dirname,
  },
  module: {
      rules: [
          {
            test: /\.css$/i,
            use: [MiniCssExtractPlugin.loader, "css-loader"],
          },
      ],
  },
  plugins: [new MiniCssExtractPlugin({
    filename: '../css/index.css'
  })]
}