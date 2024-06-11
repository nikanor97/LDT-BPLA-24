import {Project} from '..';

export type Id = string;

export type Item = {
    created_at: string;
    id: Id;
    number: string;
    project_id: Project.Id;
    updated_at: string;
    status: Status;
}

export type Status = 
    'created' |
    'in_progress' |
    'approved' | 
    'declined';
    