import update from 'immutability-helper';
import _ from 'lodash';
import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { applyMiddleware, compose, createStore } from 'redux';
import reduxThunk from 'redux-thunk';
import { actionsEnums } from './actions';
import { HoldingViewModel } from './HoldingViewModel';
import IAppState from './IAppState';
import { Guid } from './lib';

const initialState = { count: 0 };
function reducer(state = initialState, action) {
	switch (action.type) {
		default: {
			return state;
		}
	}
}

const App = () => {
	return <div />;
};
const nonTypedWindow: any = window;
const composeEnhancers =
	nonTypedWindow.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;
const store = createStore(
	reducer,
	composeEnhancers(applyMiddleware(reduxThunk)),
);

ReactDOM.render(
	<Provider store={store}>
		<App />
	</Provider>,
	document.getElementById('root'),
);
