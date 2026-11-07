export interface Vector3Dto {
    x: number
    y: number
    z: number
}

export interface QuaternionDto {
    x: number
    y: number
    z: number
    w: number
}

export interface HomeObjectCreationUpdateDto {
    name: string
    tags: string[]
    user_data: Record<string, string>
    location: Vector3Dto
    orientation: QuaternionDto
}

export interface HomeObject {
    id: string
    name: string
    creation_date: string
    tags: string[]
    user_data: Record<string, string>
    location: Vector3Dto
    orientation: QuaternionDto
}
