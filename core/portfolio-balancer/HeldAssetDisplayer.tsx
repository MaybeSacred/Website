import * as React from 'react';
import { connect } from 'react-redux';
import IAppState from './IAppState';
import { Guid } from './lib';
import { IAsset } from './types';
interface IProps {
	asset: IAsset;
	assetId: Guid;
}
interface IConvertibleProps {
	assetId: Guid;
}
const mapStateToProps = (state: IAppState, ownProps: IConvertibleProps) => {
	return {
		asset: state.assets.get(ownProps.assetId),
	};
};
const heldAssetDisplayer = (props: IProps) => {
	return (
		<>
			<input className='col-1 form-control' value={props.asset.symbol} />
			<input className='col-1 form-control' value={props.asset.price} />
		</>
	);
};
export default connect(mapStateToProps)(heldAssetDisplayer);
