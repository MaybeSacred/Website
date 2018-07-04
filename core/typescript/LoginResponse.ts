import { UserProfile } from './UserProfile';
export class LoginResponse {
	public succeeded: boolean;
	public userProfile: UserProfile;
	constructor(succeeded?: boolean, userProfile?: UserProfile) {
		this.succeeded = succeeded || false;
		this.userProfile = userProfile || new UserProfile('', '');
	}
}
