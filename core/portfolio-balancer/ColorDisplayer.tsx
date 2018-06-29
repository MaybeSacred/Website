import * as React from 'react';
import { connect } from 'react-redux';
import { AppState } from './ReactRedux';
import { IColor } from './types';
interface IProps {
	color: IColor;
}

export const ColorDisplayer = (props: IProps) => {
	const divStyle = {
		width: '120px',
		height: '80px',
		backgroundColor: `rgb(${props.color.red},${props.color.green},${
			props.color.blue
		})`,
	};
	return <div style={divStyle} />;
};
const mapStateToProps = (state: AppState) => {
	return {
		color: state.favouriteColour,
	};
};
export const ColorDisplayerContainer = connect(
	mapStateToProps,
	(dispatch) => {
		return {};
	},
)(ColorDisplayer);
