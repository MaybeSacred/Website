import * as React from 'react';
import { connect } from 'react-redux';
const LoginComponent = () => {
	return <h2>I'm the login page</h2>;
};

export const LoginContainer = connect(
	() => {
		return {};
	},
	() => {
		return {};
	},
)(LoginComponent);
