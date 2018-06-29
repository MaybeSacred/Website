import * as React from 'react';
import { connect } from 'react-redux';
import { updateUserProfileColour } from './actions';
import { ColorSlider } from './ColorSlider';
import { AppState } from './ReactRedux';
import { IColor } from './types';
interface IProps {
	color: IColor;
	onColorUpdated: (color: IColor) => void;
}

export const ColorPicker = (props: IProps) => {
	return (
		<div>
			<ColorSlider
				value={props.color.red}
				onValueUpdated={(value) =>
					props.onColorUpdated({
						red: value,
						green: props.color.green,
						blue: props.color.blue,
					})
				}
			/>
			<br />
			<ColorSlider
				value={props.color.green}
				onValueUpdated={(value) =>
					props.onColorUpdated({
						red: props.color.red,
						green: value,
						blue: props.color.blue,
					})
				}
			/>
			<br />
			<ColorSlider
				value={props.color.blue}
				onValueUpdated={(value) =>
					props.onColorUpdated({
						red: props.color.red,
						green: props.color.green,
						blue: value,
					})
				}
			/>
		</div>
	);
};

const mapStateToProps = (state: AppState) => ({ color: state.favouriteColour });
const mapDispatchToProps = (dispatch) => ({
	onColorUpdated: (color: IColor) => dispatch(updateUserProfileColour(color)),
});

export const ColorPickerContainer = connect(
	mapStateToProps,
	mapDispatchToProps,
)(ColorPicker);
