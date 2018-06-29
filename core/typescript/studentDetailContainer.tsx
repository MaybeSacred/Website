import * as React from 'react';
import { connect } from 'react-redux';
const StudentDetailComponent = () => {
	return <h2>I'm the StudentList shart</h2>;
};

export const StudentDetailContainer = connect(
	() => {
		return {};
	},
	() => {
		return {};
	},
)(StudentDetailComponent);
