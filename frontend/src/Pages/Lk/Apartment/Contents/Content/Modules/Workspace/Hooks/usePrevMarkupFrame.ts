import { getFrameTime } from "@root/Utils/Video/getFrameTime";
import { useVideo } from "../../../Hooks/useVideo";
import {Videosjs} from '@root/Types';
import { getFrameNumber } from "@root/Utils/Video/getFrameNumber";
import {ceil} from 'lodash';
import { useSelector } from "react-redux";
import {PageState} from '../../../../../Redux/types';

export const usePrevMarkupFrame = (player: Videosjs.Player | undefined, cb: (time: number) => any) => {
    const frames = useSelector((state: PageState) => state.Pages.LkApartment.videos.data?.frames);
    const video = useVideo();
    return () => {
        if (!video) return;
        if (!player) return;
        if (!frames) return;

        const progress = ceil(player.currentTime(), 4);
        const frameNumber = getFrameNumber(video, progress)
        const nextFrame = Object.values(frames)
            .reverse()
            .find((frame) => {
                if (frame.frame_offset >= frameNumber) return false;
                return frame.markups.length;
            })

        if (nextFrame === undefined) return;

        const nextTime = ceil(getFrameTime(video, nextFrame.frame_offset), 4)
        player.currentTime(nextTime)
        cb(nextTime);
    }
}