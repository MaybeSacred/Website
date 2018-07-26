import { Guid } from './lib';
export enum ActionType {
	UpdateSymbol = 'UpdateSymbol',
	UpdatePrice = 'UpdatePrice',
	UpdateCurrentShares = 'UpdateCurrentShares',
	UpdateDesiredPercentage = 'UpdateDesiredPercentage',
	UpdateDescription = 'UpdateDescription',
}

export const updateSymbol = (id: Guid, symbol: string) => {
	return {
		type: ActionType.UpdateSymbol,
		id,
		symbol,
	};
};
export const updatePrice = (id: Guid, price: number) => {
	return {
		type: ActionType.UpdatePrice,
		id,
		price,
	};
};
export const updateCurrentShares = (id: Guid, currentShares: number) => {
	return {
		type: ActionType.UpdateCurrentShares,
		id,
		currentShares,
	};
};
export const updateDesiredPercentage = (id: Guid, newPct: number) => {
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
