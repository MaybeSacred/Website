import * as React from "react";
import { IMemberEntity } from "./member";
interface IProps {
	member: IMemberEntity;
}
export const MemberRowComponent = (props: IProps) => {
	return (
		<tr>
			<td>
				<img
					src={props.member.avatar_url}
					className="avatar"
					alt="avatar"
				/>
			</td>
			<td>
				<span>{props.member.id}</span>
			</td>
			<td>
				<span>{props.member.login}</span>
			</td>
		</tr>
	);
};
