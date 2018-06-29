import { IMemberEntity } from "./member";
import { memberAPI } from "./memberAPI";
import { Color } from "./types";
export const actionsEnums = {
	incr: "INCREMENT",
	decr: "DECREMENT",
	updateUserProfileColour: "UPDATE_USERPROFILE_FAVOURITE_COLOUR",
	MEMBER_REQUEST: "MEMBER_REQUEST",
	MEMBER_REQUEST_COMPLETED: "MEMEMBER_REQUEST_COMPLETED",
};

export const updateUserProfileColour = (newColor: Color) => {
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
	const promise = memberAPI.getAllMembers();
	promise.then((data) => dispatcher(memberRequestCompleted(data)));
	return promise;
};
