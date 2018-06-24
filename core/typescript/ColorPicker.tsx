import * as React from 'react';
import { connect } from 'react-redux';
import { ColorSlider } from './ColorSlider';
import { Color, AppState, updateUserProfileColour } from './ReactRedux';
interface Props {
	color: Color;
	onColorUpdated: (color: Color) => void;
}

export const ColorPicker = (props: Props) => {
	return (
		<div>
			<ColorSlider value={props.color.red}
				onValueUpdated={(value) => props.onColorUpdated({ red: value, green: props.color.green, blue: props.color.blue })} />
			<br />
			<ColorSlider value={props.color.green}
				onValueUpdated={(value) => props.onColorUpdated({ red: props.color.red, green: value, blue: props.color.blue })} />
			<br />
			<ColorSlider value={props.color.blue}
				onValueUpdated={(value) => props.onColorUpdated({ red: props.color.red, green: props.color.green, blue: value })} />
		</div>
	);
};

const mapStateToProps = (state: AppState) => ({color: state.favouriteColour});
const mapDispatchToProps = (dispatch) => ({onColorUpdated: (color: Color) => dispatch(updateUserProfileColour(color))});

export const ColorPickerContainer = connect(mapStateToProps, mapDispatchToProps)(ColorPicker);