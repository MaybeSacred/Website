import * as React from "react";
import { connect } from "react-redux";
import { stat } from "fs";
export class AppState {
    count: number;
    favouriteColour: Color;
    constructor(count: number, favColor: Color) {
        this.count = count;
        this.favouriteColour = favColor;
    }
}
interface Props {
    count: number;
    favoriteColour: Color;
}
interface IProps {
    count: number;
    onChange: (action) => void;
}
export const actionsEnums = {
    incr: 'INCREMENT',
    decr: 'DECREMENT',
    updateUserProfileColour: 'UPDATE_USERPROFILE_FAVOURITE_COLOUR'
}
export interface Color {
    red: number;
    green: number;
    blue: number;
}
export const updateUserProfileColour = (newColor: Color) => {
    return {
        type: actionsEnums.updateUserProfileColour,
        newColor: newColor
    }
};
export class Counter extends React.Component<IProps, {}> {
    state = { count: 0 }
    constructor(prop: IProps) {
        super(prop);
    }
    increment = () => {
        this.props.onChange({ type: actionsEnums.incr });
    }
    decrement = () => {
        this.props.onChange({ type: actionsEnums.decr });
    }
    render() {
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
        favoriteColour: state.favouriteColour
    };
}
function mapDispatchToProps(dispatch) {
    return {
        onChange: (action) => dispatch(action)
    };
}
export default connect(mapStateToProps, mapDispatchToProps)(Counter);