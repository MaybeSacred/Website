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
	account: {
		id: id5,
		name: 'Roth Account',
		description: 'retirement yo',
		portfolios: [id8, id9],
	},
	portfolioIds: [id8, id9],
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
	holdingIds: [id1, id4, id7],
	holdings: new Map([
		[
			id1,
			{
				id: id1,
				portfolio: 'Main',
				assetId: id2,
				currentShares: 15,
				desiredPercentage: 20,
				description: 'you know',
			},
		],
		[
			id4,
			{
				id: id4,
				portfolio: 'Main',
				assetId: id3,
				currentShares: 10,
				desiredPercentage: 15,
				description: 'you know',
			},
		],
		[
			id7,
			{
				id: id7,
				portfolio: 'Main',
				assetId: id6,
				currentShares: 10,
				desiredPercentage: 24,
				description: 'you know',
			},
		],
	]),
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
