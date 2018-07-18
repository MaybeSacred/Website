import update from 'immutability-helper';
import * as _ from 'lodash';
import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { applyMiddleware, compose, createStore } from 'redux';
import reduxThunk from 'redux-thunk';
import { actionsEnums } from './actions';
import HoldingsContainer from './holdingsContainer';
import IAppState from './IAppState';
import { initialState } from './SampleData';

function reducer(state = initialState, action) {
	switch (action.type) {
		default: {
			return state;
		}
	}
}

const App = () => {
	return <HoldingsContainer />;
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
