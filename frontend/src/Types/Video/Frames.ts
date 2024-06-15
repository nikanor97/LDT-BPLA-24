import {Video} from '../';

export type Id = string;
export type Markup = {
    label_id: string;
    coord_top_left_x: 0
    coord_top_left_y: 0
    coord_bottom_right_x: 0
    coord_bottom_right_y: 0
    confidence: number;
}
export type Item = {
    video_id: Video.Id;
    frame_offset: number;
}

export type MarkupedItem = Item & {
    markups: Markup[];
}