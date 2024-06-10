import {Video} from '@root/Types';

export const getFrameNumber = (video:Video.Item, time: number) => {
    return Math.floor((time / video.length_sec) * video.n_frames)
}