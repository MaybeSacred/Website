import { createDefaultMemberEntity, IMemberEntity } from './member';

class MemberAPI {
	// Just return a copy of the mock data
	public getAllMembers(): Promise<IMemberEntity[]> {
		const gitHubMembersUrl: string =
			'https://api.github.com/orgs/lemoncode/members';

		return fetch(gitHubMembersUrl)
			.then((response) => this.checkStatus(response))
			.then((response) => this.parseJSON(response))
			.then((data) => this.resolveMembers(data));
	}

	private checkStatus(response: Response): Promise<Response> {
		if (response.status >= 200 && response.status < 300) {
			return Promise.resolve(response);
		} else {
			const error = new Error(response.statusText);
			throw error;
		}
	}

	private parseJSON(response: Response): any {
		return response.json();
	}

	private resolveMembers(data: any): Promise<IMemberEntity[]> {
		const members = data.map((gitHubMember) => {
			const member: IMemberEntity = createDefaultMemberEntity();

			member.id = gitHubMember.id;
			member.login = gitHubMember.login;
			member.avatar_url = gitHubMember.avatar_url;

			return member;
		});

		return Promise.resolve(members);
	}
}

export const memberAPI = new MemberAPI();
