import {RequestFullState, RequestShortState} from "@root/Utils/Redux/RequestState/types";
import {PageStateGeneric} from '@root/Redux/store';
import {Slice} from './Store';
import {Api} from '@root/Api/Projects/types';
import {Viewer, Video, Project, Photo} from '@root/Types';


export declare namespace iState {
    type VideosState = {
        info: Video.Item | Photo.Item | null;
        frames: {
            [key: number]: Video.Frames.MarkupedItem;
        } | null;
    }
    type PlayInterval = {
        start: number;
        end: number;
        key: string;
    }
    type Labels = {
        [key: string]: Project.Label.Item;
    }
    type Value = {
        content: RequestFullState<VideosState>;
        labels: RequestFullState<Labels>;
        playInterval: PlayInterval | null;
        videoStatus: RequestShortState;
        content_ids: RequestFullState<(Video.Item['content_id'] | Photo.Item['content_id'])[]>;
    }
}


export declare namespace iActions {
    type getContentInfo = Api.iGetContentInfo;
    type _getContentInfoSuccess = iState.VideosState;

    type getContentIds = Api.iGetContentIds;
    type _getContentIdsSuccess = (Video.Item['content_id'] | Photo.Item['content_id'])[];

    type getLabels = Api.iGetLabels;
    type _getLabelsSuccess = iState.Labels
    
    type updateVideoMeta = Partial<Video.Item>

    type setPlayInterval = iState.PlayInterval | null;
    type changeContentStatus = Api.iChangeContentStatus;
    type _changeContenttatusSuccess = Api.oChangeContentStatus;
    type setImageIndex = number;
    type downloadResult = {
        content_id: (Video.Item['content_id'] | Photo.Item['content_id']);
    }
}

export type PageState = PageStateGeneric<{
    [Slice.name]: ReturnType<typeof Slice.reducer>
}>