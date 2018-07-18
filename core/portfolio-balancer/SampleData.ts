import { newGuid } from './lib';

const id1 = newGuid();
const id2 = newGuid();
const id3 = newGuid();
const id4 = newGuid();
const id5 = newGuid();
const id6 = newGuid();
const id7 = newGuid();
const id8 = newGuid();
const id9 = newGuid();
const initialState = {
	accounts: [
		{
			id: id5,
			name: 'Roth Account',
			description: 'retirement yo',
			portfolios: [id8, id9],
		},
	],
	portfolios: [
		{
			id: id8,
			name: 'Roth Account',
			description: 'retirement yo',
			portfolios: [id1, id4],
		},
		{
			id: id9,
			name: 'Coin desk',
			description: 'for fun yo',
			portfolios: [id7],
		},
	],
	holdingIds: [id1, id4],
	holdings: [
		{
			id: id1,
			portfolio: 'Main',
			assetId: id2,
			currentShares: 15,
			desiredShares: 13,
			currentPercentage: 0.04,
			desiredPercentage: 0.20,
			description: 'you know',
		},
		{
			id: id4,
			portfolio: 'Main',
			assetId: id3,
			currentShares: 10,
			desiredShares: 13,
			currentPercentage: 0.16,
			desiredPercentage: 0.15,
			description: 'you know',
		},
		{
			id: id7,
			portfolio: 'Main',
			assetId: id6,
			currentShares: 10,
			desiredShares: 13,
			currentPercentage: 0.04,
			desiredPercentage: 0.24,
			description: 'you know',
		},
	],
	assets: new Map([
		[
			id2,
			{
				id: id2,
				symbol: 'VOO',
				price: 250.6,
			},
		],
		[
			id3,
			{
				id: id3,
				symbol: 'GLD',
				price: 1200.1,
			},
		],
		[
			id6,
			{
				id: id6,
				symbol: 'BTC',
				price: 6000.1,
			},
		],
	]),
};
export { initialState };
