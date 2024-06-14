import {useSelector} from "react-redux"
import {PageState} from '../../../../../../../Redux/types';
import { usePhoto } from "../../../../../Hooks/usePhoto";
import {LabelGrouped} from '../types';

export const useFramesByLabels = () => {
    const labels = useSelector((state:PageState) => state.Pages.LkViewer.labels.data)
    const frames = useSelector((state:PageState) => state.Pages.LkViewer.content.data?.frames)
    const video = usePhoto();

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
                    frameNumber: frame.frame_offset
                })
            })
        })
    return result;
}