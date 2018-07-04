export class LoginEntity {
	public login = '';
	public password = '';
	public constructor(login?: string, password?: string) {
		this.login = login || '';
		this.password = password || '';
	}
}
