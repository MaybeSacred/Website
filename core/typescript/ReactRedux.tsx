import * as React from "react";
import { connect } from "react-redux";
import { MemberEntity } from "./member";
import { actionsEnums, } from './actions';
import { memberAPI } from './memberAPI';
import { Color } from './types';
export class AppState {
    count: number;
    favouriteColour: Color;
    members: MemberEntity[];
    constructor(count: number, favColor: Color, members: MemberEntity[]) {
        this.count = count;
        this.favouriteColour = favColor;
        this.members = members;
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