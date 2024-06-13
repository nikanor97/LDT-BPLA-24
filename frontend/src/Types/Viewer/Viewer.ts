import {Project, Photo, Video} from '..';

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


export const isVideoItem = (item: Video.Item | Photo.Item | null | undefined): item is Video.Item => {
    if (!item) return false
    return item.content_type === 'video';
}
    
export const isPhotoItem = (item: Video.Item | Photo.Item | null | undefined): item is Photo.Item => {
    if (!item) return false
    return item.content_type === 'photo';
}