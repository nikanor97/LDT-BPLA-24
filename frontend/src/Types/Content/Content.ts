import {Photo, Video} from '../';

export type Item = Photo.Item | Video.Item;

export type Status = 
    'created' |
    'in_progress' |
    'approved' | 
    'declined';