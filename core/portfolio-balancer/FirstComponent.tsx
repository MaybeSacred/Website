import * as React from "react";
const Logo = "https://logrocket.com/img/logo.png";
class User {
	public firstName: string;
	public lastName: string;
	constructor(firstName: string, lastName: string) {
		this.firstName = firstName;
		this.lastName = lastName;
	}
}
function formatName(user: User) {
	return `${user.firstName} ${user.lastName}`;
}

export class FirstComponent extends React.Component<{}> {
	public render() {
		return (
			<div>
				<h1>A simple component</h1>
				<div>
					<img src={Logo} />
				</div>
				<p>{formatName(new User("Jon", "Bronk"))}</p>
			</div>
		);
	}
}
