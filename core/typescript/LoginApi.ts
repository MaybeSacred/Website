import { LoginEntity } from './LoginEntity';
import { LoginResponse } from './LoginResponse';
import { UserProfile } from './userProfile';

class LoginApi {
	public login(LoginInfo: LoginEntity): Promise<LoginResponse> {
		const response = new LoginResponse();
		if (LoginInfo.login === 'admin' && LoginInfo.password === 'test') {
			response.succeeded = true;
			response.userProfile = new UserProfile('John Doe', 'admin');
		} else {
			response.succeeded = false;
			response.userProfile = new UserProfile();
		}
		return Promise.resolve(response);
	}
}
export const loginApi = new LoginApi();
