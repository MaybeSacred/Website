import { ActionType } from './actions';
import { initialState } from './SampleData';

export const reducer = (state = initialState, action) => {
	switch (action.type) {
		case ActionType.UpdateDesiredPercentage: {
			return {
				...state,
				holdings: state.holdings.set(
					action.id,
					Object.assign({}, state.holdings.get(action.id), {
						desiredPercentage: action.newPct,
					}),
				),
			};
		}
		default:
			return state;
	}
};
