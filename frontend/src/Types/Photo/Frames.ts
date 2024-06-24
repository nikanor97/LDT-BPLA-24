import {Photo} from '../';

export type Id = string;
export type Markup = {
    id: string;
    frame_id: Id;
    label_id: string;
    coord_top_left_x: number
    coord_top_left_y: number
    coord_bottom_right_x: number
    coord_bottom_right_y: number
    confidence: number;
}
export type Item = {
    photo_id: Photo.Id;
    frame_offset: number;
    id: Id;
}

export type MarkupedItem = Item & {
    markups: Markup[];
}