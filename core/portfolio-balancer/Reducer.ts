import { ActionType } from './actions';
import IAppState from './IAppState';
import { Guid } from './lib';
import { initialState } from './SampleData';

const updateIHoldingProperty = (state: IAppState, id: Guid, property: any) => {
	return {
		...state,
		holdings: state.holdings.set(
			id,
			Object.assign({}, state.holdings.get(id), property),
		),
	};
};

export const reducer = (state = initialState, action) => {
	switch (action.type) {
		case ActionType.UpdatePortfolioTotalValue: {
			return {
				...state,
				portfolios: state.portfolios.set(
					action.id,
					Object.assign({}, state.portfolios.get(action.id), {totalValue: action.totalValue}),
				),
			};
		}
		case ActionType.UpdateSymbol: {
			return updateIHoldingProperty(state, action.id, {
				symbol: action.symbol,
			});
		}
		case ActionType.UpdatePrice: {
			return updateIHoldingProperty(state, action.id, {
				price: action.price,
			});
		}
		case ActionType.UpdateCurrentShares: {
			return updateIHoldingProperty(state, action.id, {
				currentShares: action.currentShares,
			});
		}
		case ActionType.UpdateDesiredPercentage: {
			return updateIHoldingProperty(state, action.id, {
				desiredPercentage: action.newPct,
			});
		}
		case ActionType.UpdateDescription: {
			return updateIHoldingProperty(state, action.id, {
				description: action.description,
			});
		}
		default:
			return state;
	}
};
