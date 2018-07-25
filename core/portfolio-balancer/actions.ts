import { Guid } from './lib';
export enum ActionType {
	UpdateDesiredPercentage = 'UpdateDesiredPercentage',
}

export const updateDesiredPercentage = (id: Guid, newPct: number) => {
	return {
		type: ActionType.UpdateDesiredPercentage,
		id,
		newPct,
	};
};
