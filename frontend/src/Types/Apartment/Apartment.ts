import {Project} from '../';

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


export declare namespace Scores {
    type LeafItem = {
        value: string;
        label: string;
    }
    type NodeItem = {
        label: string;
        value: {
            [key: string]: NodeItem | LeafItem;
        }
    }

    type Result = {
        [key: string]: LeafItem | NodeItem;
    }
}

export const Guards = {
    Scores: {
        isNode: (item: Scores.LeafItem | Scores.NodeItem): item is Scores.NodeItem => typeof item.value === 'object'
    }
}