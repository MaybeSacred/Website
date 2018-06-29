const path = require("path");
const webpack = require("webpack");
const UglifyJSPlugin = require("uglifyjs-webpack-plugin");
var config = (env, argv) => {
	return {
		entry: {
			app: "./typescript/app.tsx",
			"portfolio-balancer": "./portfolio-balancer/app.tsx"
		},
		output: {
			path: path.resolve(__dirname, "../public"),
			filename: "[name].bundle.js"
		},
		resolve: {
			extensions: [".ts", ".tsx", ".js", ".jsx"]
		},
		mode: argv.mode || "development",
		module: {
			rules: [
				{
					test: /\.tsx?$/,
					loader: "ts-loader",
					exclude: /node_modules/
				},
				{
					test: /\.css$/,
					use: ["style-loader", "css-loader"]
				}
			]
		},
		plugins: [
			new webpack.DefinePlugin({
				"process.env.NODE_ENV": JSON.stringify(
					argv.mode || "development"
				)
			}),
			new UglifyJSPlugin({ sourceMap: true })
		]
	};
};
module.exports = config;
