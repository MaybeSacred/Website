export class UserProfile {
	public fullname: string;
	public role: string;
	constructor(fullName?: string, role?: string) {
		this.fullname = fullName || '';
		this.role = role || '';
	}
}
