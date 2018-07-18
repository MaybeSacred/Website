// import { actionsEnums } from './actions';
// import { LoginEntity } from '../model/login';
// import { LoginResponse } from '../model/loginResponse';
// import { UserProfile } from '../model/userProfile';

// class SessionState {
// 	public isUserLoggedIn: boolean;
// 	public userProfile: UserProfile;
// 	public editingLogin: LoginEntity;

// 	public constructor() {
// 		this.isUserLoggedIn = false;
// 		this.userProfile = new UserProfile();
// 		this.editingLogin = new LoginEntity();
// 	}
// }

// export const sessionReducer = (
// 	state: SessionState = new SessionState(),
// 	action,
// ) => {
// 	switch (action.type) {
// 		case actionsEnums.USERPROFILE_PERFORM_LOGIN:
// 			return handlePerformLogin(state, action.payload);
// 		case actionsEnums.USERPROFILE_UPDATE_EDITING_LOGIN:
// 			return handleUpdateEditingLogin(state, action.payload);
// 	}

// 	return state;
// };

// const handlePerformLogin = (state: SessionState, payload: LoginResponse) => {
// 	return {
// 		...state,
// 		isUserLoggedIn: payload.succeeded,
// 		userProfile: payload.userProfile,
// 	};
// };

// const handleUpdateEditingLogin = (
// 	state: SessionState,
// 	payload: LoginEntity,
// ) => {
// 	const newState = {
// 		...state,
// 		editingLogin: payload,
// 	};

// 	return newState;
// };
