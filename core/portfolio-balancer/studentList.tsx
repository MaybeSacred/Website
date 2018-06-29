import * as React from 'react';
import { connect } from 'react-redux';
const StudentListComponent = () => {
	return <h2>I'm the StudentList shart</h2>;
};

export const StudentListContainer = connect(
	() => {
		return {};
	},
	() => {
		return {};
	},
)(StudentListComponent);
