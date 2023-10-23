const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
let LiveReloadPlugin = require('webpack-livereload-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin')

const mode = process.argv.indexOf("production") !== -1 ? "production" : "development";
console.log(`Webpack mode: ${mode}`);

module.exports = {
  entry: './qgisfeedproject/static/js/index',
  output: {
    path: path.resolve('./qgisfeedproject/static/bundles'),
    filename: "bundle.js"
  },
  plugins: [
    new LiveReloadPlugin({appendScriptTag: true}),
    new BundleTracker({path: __dirname, filename: 'webpack-stats.json'}),
    new MiniCssExtractPlugin({
        filename: 'css/style.css'
    }),
  ],
  module: {
    rules: [
      {
        test: /\.scss$/,
        use: [
            MiniCssExtractPlugin.loader,
            {
              loader: 'css-loader'
            },
            {
              loader: 'sass-loader',
              options: {
                sourceMap: true
              }
            }
          ]
      }
    ],
  },
};
