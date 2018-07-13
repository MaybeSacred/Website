import { hashHistory } from 'react-router';
import { loginApi } from './LoginApi';
import { LoginEntity } from './LoginEntity';
import { LoginResponse } from './LoginResponse';
import { IMemberEntity } from './member';
import { memberAPI } from './memberAPI';
import { IColor } from './types';
export const actionsEnums = {
	incr: 'INCREMENT',
	decr: 'DECREMENT',
	updateUserProfileColour: 'UPDATE_USERPROFILE_FAVOURITE_COLOUR',
	MEMBER_REQUEST: 'MEMBER_REQUEST',
	MEMBER_REQUEST_COMPLETED: 'MEMEMBER_REQUEST_COMPLETED',
	USERPROFILE_PERFORM_LOGIN: 'USERPROFILE_PERFORM_LOGIN',
	USERPROFILE_UPDATE_EDITING_LOGIN: 'USERPROFILE_UPDATE_EDITING_LOGIN',
};

export const loginRequestCompletedAction = (loginResponse: LoginResponse) => {
	return {
		type: actionsEnums.USERPROFILE_PERFORM_LOGIN,
		payload: loginResponse,
	};
};
export const loginRequestStartedAction = (login: LoginEntity) => {
	return (dispatcher) => {
		return loginApi.login(login).then((data) => {
			dispatcher(loginRequestCompletedAction(data));
			if (data.succeeded) {
				hashHistory.push('./student-list');
			}
		});
	};
};
export const updateUserProfileColour = (newColor: IColor) => {
	return {
		type: actionsEnums.updateUserProfileColour,
		newColor,
	};
};
export const memberRequestCompleted = (members: IMemberEntity[]) => {
	return {
		type: actionsEnums.MEMBER_REQUEST_COMPLETED,
		members,
	};
};

export const memberRequest = () => (dispatcher) => {
	return memberAPI
		.getAllMembers()
		.then((data) => dispatcher(memberRequestCompleted(data)));
};
