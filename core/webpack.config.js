const path = require("path");
const webpack = require('webpack');
const UglifyJSPlugin = require('uglifyjs-webpack-plugin');
var config = {
  entry: ["./typescript/app.tsx"],
  output: {
    path: path.resolve(__dirname, "../public"),
    filename: "bundle.js"
  },
  devtool: "source-map",
  resolve: {
    extensions: [".ts", ".tsx", ".js"]
  },
  mode: "production",
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        loader: "ts-loader",
        exclude: /node_modules/
      }
    ]
  },
  plugins: [
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify('production')
    }),
    new UglifyJSPlugin({sourceMap: true})
  ]
};

module.exports = config;