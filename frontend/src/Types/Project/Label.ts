import {Project} from '../';

export type Id = string;
export type Item = {
    id: Id;
    created_at: string;
    updated_at: string;
    name: string;
    description: string;
    color: string;
    project_id: Project.Id;
}