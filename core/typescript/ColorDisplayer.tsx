import * as React from 'react';
import { connect } from 'react-redux';
import { Color, AppState } from './ReactRedux';
interface Props {
	color: Color;
}

export const ColorDisplayer = (props: Props) => {
	let divStyle = {
		width: "120px",
		height: "80px",
		backgroundColor: `rgb(${props.color.red},${props.color.green},${props.color.blue})`
	};
	return (
		<div style={divStyle}></div>
	)
};
const mapStateToProps = (state: AppState) => {
	return {
		color: state.favouriteColour
	};
};
export const ColorDisplayerContainer = connect(mapStateToProps, (dispatch) => { return {}; })(ColorDisplayer);