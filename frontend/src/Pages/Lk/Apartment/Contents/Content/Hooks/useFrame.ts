import {useRef} from 'react';
import {useSelector} from "react-redux";
import {useFrameNumber} from "./useFrameNumber"
import {PageState} from '../../../Redux/types';
import {Video} from '@root/Types';

const delta = 3;


export const useFrame = (progres: number) => {
    const lastFrame = useRef<Video.Frames.MarkupedItem>(null);
    const frameNumber = useFrameNumber(progres);
    const frames = useSelector((state:PageState) => state.Pages.LkApartment.videos.data?.frames)
    if (!frames) return null;
    if (frameNumber in frames) {
        //@ts-ignore
        lastFrame.current = frames[frameNumber];
        return frames[frameNumber];
    } else {
        if (lastFrame.current) {
            if (lastFrame.current.frame_offset > frameNumber) return null;
            if (frameNumber - lastFrame.current.frame_offset < delta) {
                return lastFrame.current
            } else {
                return null;
            }
        }
        return null;
    }
    
}