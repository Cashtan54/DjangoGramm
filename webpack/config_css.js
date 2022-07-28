const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');


module.exports = {
  entry: './src/css/main_css.js',
  mode: 'development',
  module: {
      rules: [
          {
            test: /\.css$/i,
            use: [MiniCssExtractPlugin.loader, "css-loader"],
          },
      ],
  },
  plugins: [new MiniCssExtractPlugin({
    filename: './index.css'
  })]
}