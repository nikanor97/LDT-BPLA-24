import { getFrameNumber } from "@root/Utils/Video/getFrameNumber";
import {useVideo} from "./useVideo"



export const useFrameNumber = (progress: number) => {
    const video = useVideo();
    if (!video) return 0;
    return getFrameNumber(video, progress);
}