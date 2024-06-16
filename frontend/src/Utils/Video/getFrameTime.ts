import {Video} from '@root/Types';

export const getFrameTime = (video:Video.Item, frame: number) => {
    if (frame >= video.n_frames) return video.length_sec;
    if (frame <= 0) return 0;
    const time = frame / video.n_frames * video.length_sec;
    return time;
}
