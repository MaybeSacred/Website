import update from "immutability-helper";
import * as _ from "lodash";
import * as React from "react";
import * as ReactDOM from "react-dom";
import { Provider } from "react-redux";
import { applyMiddleware, compose, createStore } from "redux";
import reduxThunk from "redux-thunk";
import { actionsEnums } from "./actions";
import { ColorDisplayerContainer } from "./ColorDisplayer";
import { ColorPickerContainer } from "./ColorPicker";
import { FirstComponent } from "./FirstComponent";
import { Asset, Guid, Holding } from "./Holding";
import { HoldingViewModel } from "./HoldingViewModel";
import { MembersAreaContainer } from "./memberArea";
import { AppState } from "./ReactRedux";
import Counter from "./ReactRedux";

const initialState = new AppState(0, { red: 0, green: 0, blue: 180 }, []);
function reducer(state = initialState, action) {
	switch (action.type) {
		case actionsEnums.incr: {
			return new AppState(
				state.count + 1,
				state.favouriteColour,
				state.members
			);
		}
		case actionsEnums.decr: {
			return new AppState(
				state.count - 1,
				state.favouriteColour,
				state.members
			);
		}
		case actionsEnums.updateUserProfileColour: {
			return new AppState(state.count, action.newColor, state.members);
		}
		case actionsEnums.MEMBER_REQUEST_COMPLETED: {
			return new AppState(
				state.count,
				state.favouriteColour,
				action.members
			);
		}
		default: {
			return state;
		}
	}
}

const App = () => {
	return (
		<div>
			<MembersAreaContainer />
			<br />
			<Counter />
			<br />
			<ColorDisplayerContainer />
			<br />
			<ColorPickerContainer />
		</div>
	);
};
const nonTypedWindow: any = window;
const composeEnhancers =
	nonTypedWindow.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;
const store = createStore(
	reducer,
	composeEnhancers(applyMiddleware(reduxThunk))
);

ReactDOM.render(
	<Provider store={store}>
		<App />
	</Provider>,
	document.getElementById("root")
);
