import * as React from 'react';
import { IMemberEntity } from './member';
import { MemberRowComponent } from './memberRow';
interface IProps {
	members: IMemberEntity[];
}
export const MemberTableComponent = (props: IProps) => {
	return (
		<div>
			<h2>Members Page</h2>
			<table className='table'>
				<thead>
					<tr>
						<th>Avatar</th>
						<th>Id</th>
						<th>Name</th>
					</tr>
				</thead>
				<tbody>
					{props.members.map((member: IMemberEntity) => (
						<MemberRowComponent key={member.id} member={member} />
					))}
				</tbody>
			</table>
		</div>
	);
};
