import * as React from "react";
interface IProps {
	value: number;
	onValueUpdated: (newValue: number) => void;
}

export const ColorSlider = (props: IProps) => {
	return (
		<div>
			<input
				type="range"
				min="0"
				max="255"
				value={props.value}
				onChange={(event) =>
					props.onValueUpdated(parseInt(event.target.value, 10))
				}
			/>
			{props.value}
		</div>
	);
};
