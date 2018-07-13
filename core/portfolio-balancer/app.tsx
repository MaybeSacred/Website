import update from 'immutability-helper';
import _ from 'lodash';
import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { applyMiddleware, compose, createStore } from 'redux';
import reduxThunk from 'redux-thunk';
import { actionsEnums } from './actions';
import { Asset } from './Asset';
import { Holding } from './Holding';
import HoldingsContainer from './holdingsContainer';
import { HoldingViewModel } from './HoldingViewModel';
import IAppState from './IAppState';
import { Guid } from './lib';
const id1 = Guid.new();
const id2 = Guid.new();
const initialState = {
	holdingIds: [],
	holdings: [
		{
			id: id1,
			portfolio: 'Main',
			assetId: id2,
			currentShares: '15',
			desiredShares: '13',
			currentPercentage: '4',
			desiredPercentage: '3',
			description: 'you know',
		},
	],
	assets: [
		{
			id: id2,
			symbol: 'VOO',
			price: 25.6,
		},
	],
};
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
