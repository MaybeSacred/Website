const path = require("path");
const webpack = require("webpack");
var config = (env, argv) => {
	return {
		entry: {
			//app: "./typescript/main.tsx",
			"portfolio-balancer": "./portfolio-balancer/app.tsx"
		},
		output: {
			path: path.resolve(__dirname, "../public"),
			filename: "[name].bundle.js"
		},
		optimization:{

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
					exclude: /(node_modules|typescript)/
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
		]
	};
};
module.exports = config;
