import { routerReducer } from 'react-router-redux';
import { combineReducers } from 'redux';
import { sessionReducer } from './session';

export const reducers = combineReducers({
	sessionReducer,
	routing: routerReducer,
});
