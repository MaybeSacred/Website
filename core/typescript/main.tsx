import update from 'immutability-helper';
import * as _ from 'lodash';
import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { hashHistory, IndexRoute, Link, Route, Router } from 'react-router';
import { syncHistoryWithStore } from 'react-router-redux';
import { applyMiddleware, compose, createStore } from 'redux';
import reduxThunk from 'redux-thunk';
import { actionsEnums } from './actions';
import { ColorDisplayerContainer } from './ColorDisplayer';
import { ColorPickerContainer } from './ColorPicker';
import { LoginContainer } from './login';
import { MembersAreaContainer } from './memberArea';
import { AppState } from './ReactRedux';
import Counter from './ReactRedux';
import { StudentDetailContainer } from './studentDetailContainer';
import { StudentListContainer } from './studentList';
const Header = () => {
	return (
		<div className='panel-heading'>
			<h3 className='panel-title'>Please sign in</h3>
		</div>
	);
};
const initialState = new AppState(0, { red: 0, green: 0, blue: 180 }, []);
function reducer(state = initialState, action) {
	switch (action.type) {
		case actionsEnums.incr: {
			return new AppState(
				state.count + 1,
				state.favouriteColour,
				state.members,
			);
		}
		case actionsEnums.decr: {
			return new AppState(
				state.count - 1,
				state.favouriteColour,
				state.members,
			);
		}
		case actionsEnums.updateUserProfileColour: {
			return new AppState(state.count, action.newColor, state.members);
		}
		case actionsEnums.MEMBER_REQUEST_COMPLETED: {
			return new AppState(
				state.count,
				state.favouriteColour,
				action.members,
			);
		}
		default: {
			return state;
		}
	}
}

const nonTypedWindow: any = window;
const devToolsExtension = 'devToolsExtension';
const composeEnhancers =
	nonTypedWindow.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;
const store = createStore(
	reducer,
	compose(
		applyMiddleware(reduxThunk),
		window[devToolsExtension] ? window[devToolsExtension]() : (f) => f,
	),
); // component={App}>
const history = syncHistoryWithStore(hashHistory, store);
ReactDOM.render(
	<div>
		<Router history={history}>
			<Route path='/'>
				<IndexRoute component={LoginContainer} />
				<Route path='login' component={LoginContainer} />
				<Route path='student-list' component={StudentListContainer} />
				<Route
					path='student-detail'
					component={StudentDetailContainer}
				/>
			</Route>
		</Router>
	</div>,
	document.getElementById('root'),
);
