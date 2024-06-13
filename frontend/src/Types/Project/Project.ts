import {User} from '../'

export type Role = 
    'author' | 
    'view_only' | 
    'verificator';

export type Id = string;
export type Item = {
    user_id: User.Id;
    project_id: Id;
    role_type: Role;
    id: Id;
    user: User.Info;
    project: Info;
}
export type RoleGroupedItem = Omit<Item, 'role_type'> & {
    role_type: Role[]
}

export type Status =
    'created' | 
    'in_progress' | 
    'finished';

export type Info = {
    id: Id;
    created_at: string;
    updated_at: string;
    name: string,
    status: Status;
    is_deleted: boolean;
}


export type ItemFull = {
    name: string,
    status: Status
    is_deleted: boolean,
    author: User.Info
    created_at: string;
    id: Id;
    type: string;
    detected_count: number;
    msg_receiver: string
}

export declare namespace Tags {
    type Id = string;
    type Item = {
        created_at: string;
        groupname: string;
        id: Id;
        tagname: string;
        updated_at: string;
    }
}