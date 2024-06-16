import {Project, Video} from '@root/Types';

export type LabelGrouped = {
    label: Project.Label.Item;
    results: {
        frame: Video.Frames.MarkupedItem;
        markup: Video.Frames.Markup;
        time: number;
        frameNumber: number;
    }[];
}


type LabelInterval = {
    start: number;
    end: number;
    results: IntervalItem[];
}

type IntervalItem = {
    frame: Video.Frames.MarkupedItem;
    markup: Video.Frames.Markup
}

export type LabelIntervals = {
    result: LabelInterval[];
    start: number | null;
    current: number | null;
    buffer: IntervalItem[];
    label: Project.Label.Item | null;
    framesCount: number;
}