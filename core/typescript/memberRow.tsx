import * as React from 'react';
import {MemberEntity} from './member';
interface Props {
	member: MemberEntity
}
export const MemberRowComponent = (props: Props) => {
	return (
		<tr>
			<td><img src={props.member.avatar_url} alt="avatar"/></td>
		</tr>
	);
};