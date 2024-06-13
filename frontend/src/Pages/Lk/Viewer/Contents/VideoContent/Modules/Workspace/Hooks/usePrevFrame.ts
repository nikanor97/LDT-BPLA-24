import { getFrameTime } from "@root/Utils/Video/getFrameTime";
import { useVideo } from "../../../Hooks/useVideo";
import {Videosjs} from '@root/Types';
import { getFrameNumber } from "@root/Utils/Video/getFrameNumber";
import {ceil} from 'lodash';


export const usePrevFrame = (player: Videosjs.Player | undefined, cb: (time: number) => any) => {
    const video = useVideo();
    return () => {
        if (!video) return;
        if (!player) return;

        const progress = ceil(player.currentTime(), 4);
        const frameNumber = getFrameNumber(video, progress)
        const nextTime = ceil(getFrameTime(video, frameNumber - 1), 4)
        player.currentTime(nextTime)
        cb(nextTime)
    }
}