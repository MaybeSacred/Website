import * as React from 'react';
import { connect } from 'react-redux';
import { memberRequest } from './actions';
import { IMemberEntity } from './member';
import { MemberTableComponent } from './memberTable';
import { AppState } from './ReactRedux';

interface IProps {
	members: IMemberEntity[];
	loadMembers: () => any;
}

export const MemberAreaComponent = (props: IProps) => {
	return (
		<div>
			<MemberTableComponent members={props.members} />
			<br />
			<input
				type='submit'
				value='load'
				className='btn btn-default'
				onClick={() => props.loadMembers()}
			/>
		</div>
	);
};

const mapStateToProps = (state: AppState) => {
	return {
		members: state.members,
	};
};
const mapDispatchToProps = (dispatch) => {
	return {
		loadMembers: () => {
			return dispatch(memberRequest());
		},
	};
};

export const MembersAreaContainer = connect(
	mapStateToProps,
	mapDispatchToProps,
)(MemberAreaComponent);
