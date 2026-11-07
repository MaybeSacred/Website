import type { Vector3Dto } from './homeObject'

export interface GroupCreationDto {
    name: string
    points: Vector3Dto[]
}

export interface MapGroup extends GroupCreationDto {
    id: string
    creation_date: string
}
