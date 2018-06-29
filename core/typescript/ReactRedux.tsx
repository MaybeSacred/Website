import * as React from 'react';
import { connect } from 'react-redux';
import { actionsEnums } from './actions';
import { IMemberEntity } from './member';
import { memberAPI } from './memberAPI';
import { Color } from './types';
export class AppState {
	public count: number;
	public favouriteColour: Color;
	public members: IMemberEntity[];
	constructor(count: number, favColor: Color, members: IMemberEntity[]) {
		this.count = count;
		this.favouriteColour = favColor;
		this.members = members;
	}
}

interface IProps {
	count: number;
	favoriteColour: Color;
	onChange: (action) => void;
}

export class Counter extends React.Component<IProps, {}> {
	public state = { count: 0 };
	constructor(prop: IProps) {
		super(prop);
	}
	public increment = () => {
		this.props.onChange({ type: actionsEnums.incr });
	}
	public decrement = () => {
		this.props.onChange({ type: actionsEnums.decr });
	}
	public render() {
		return (
			<div>
				<h2>Counter</h2>
				<div>
					<button onClick={this.decrement}>-</button>
					<span>{this.props.count}</span>
					<button onClick={this.increment}>+</button>
				</div>
			</div>
		);
	}
}
function mapStateToProps(state: AppState) {
	return {
		count: state.count,
		favoriteColour: state.favouriteColour,
	};
}
function mapDispatchToProps(dispatch) {
	return {
		onChange: (action) => dispatch(action),
	};
}
export default connect(
	mapStateToProps,
	mapDispatchToProps,
)(Counter);
