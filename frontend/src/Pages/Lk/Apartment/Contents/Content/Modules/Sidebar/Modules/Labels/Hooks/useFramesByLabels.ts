import {useSelector} from "react-redux"
import {PageState} from '../../../../../../../Redux/types';
import { getFrameTime } from "@root/Utils/Video/getFrameTime";
import { useVideo } from "../../../../../Hooks/useVideo";
import {LabelGrouped} from '../types';

export const useFramesByLabels = () => {
    const labels = useSelector((state:PageState) => state.Pages.LkApartment.labels.data)
    const frames = useSelector((state:PageState) => state.Pages.LkApartment.videos.data?.frames)
    const video = useVideo();

    if (!labels) return null;
    if (!frames) return null;
    if (!video) return null;

    const result: {[key: string]: LabelGrouped} = {}

    Object.values(frames)
        .forEach((frame) => {
            frame.markups.forEach((markup) => {
                const id = markup.label_id;
                if (!(id in result)) result[id] = {
                    label: labels[id],
                    results: []
                };

                result[id].results.push({
                    frame,
                    markup,
                    time: getFrameTime(video,frame.frame_offset),
                    frameNumber: frame.frame_offset
                })
            })
        })
    return result;
}