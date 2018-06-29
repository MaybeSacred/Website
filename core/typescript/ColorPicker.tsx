import * as React from "react";
import { connect } from "react-redux";
import { updateUserProfileColour } from "./actions";
import { ColorSlider } from "./ColorSlider";
import { AppState } from "./ReactRedux";
import { Color } from "./types";
interface IProps {
	color: Color;
	onColorUpdated: (color: Color) => void;
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
	onColorUpdated: (color: Color) => dispatch(updateUserProfileColour(color)),
});

export const ColorPickerContainer = connect(
	mapStateToProps,
	mapDispatchToProps,
)(ColorPicker);
