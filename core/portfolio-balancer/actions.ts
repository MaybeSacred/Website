import * as numeral from 'numeral';
import { Guid } from './lib';
export enum ActionType {
	UpdatePortfolioTotalValue= 'UpdatePortfolioTotalValue',
	UpdateSymbol = 'UpdateSymbol',
	UpdatePrice = 'UpdatePrice',
	UpdateCurrentShares = 'UpdateCurrentShares',
	UpdateDesiredPercentage = 'UpdateDesiredPercentage',
	UpdateDescription = 'UpdateDescription',
}
export interface IAction {
	type: ActionType;
	payload: any;
}
export const updatePortfolioTotalValue = (id: Guid, totalValue: Numeral) => {
	return {
		type: ActionType.UpdatePortfolioTotalValue,
		id,
		totalValue: isNaN(totalValue.value()) ? 0 : totalValue.value(),
	};
};
export const updateSymbol = (id: Guid, symbol: string) => {
	return {
		type: ActionType.UpdateSymbol,
		id,
		symbol,
	};
};
export const updatePrice = (id: Guid, price: string) => {
	const val = numeral(price);
	return {
		type: ActionType.UpdatePrice,
		id,
		price: isNaN(val.value()) ? 0 : val.value(),
	};
};
export const updateCurrentShares = (id: Guid, currentShares: string) => {
	return {
		type: ActionType.UpdateCurrentShares,
		id,
		currentShares,
	};
};
export const updateDesiredPercentage = (id: Guid, newPct: string) => {
	return {
		type: ActionType.UpdateDesiredPercentage,
		id,
		newPct,
	};
};
export const updateDescription = (id: Guid, description: string) => {
	return {
		type: ActionType.UpdateDescription,
		id,
		description,
	};
};
