import {RequestFullState, RequestShortState} from "@root/Utils/Redux/RequestState/types";
import {PageStateGeneric} from '@root/Redux/store';
import {Slice} from './Store';
import {Api} from '@root/Api/Projects/types';
import {Viewer, Video, Project, Photo} from '@root/Types';
import { Markup } from "@root/Types/Photo/Frames";


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
        viewMode: "markup" | "result",
        photoMarkup: {
            newMarkups: Omit<Photo.Frames.Markup, "confidence">[],
            changedMarkups: string[],
            selectedLabel: Project.Label.Item | null;
        }
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
    type changeContentStatus = Api.iChangeContentStatus & {
        onSuccess?: () => void
    };
    type _changeContenttatusSuccess = Api.oChangeContentStatus;
    type setImageIndex = number;
    type downloadResult = {
        content_id: (Video.Item['content_id'] | Photo.Item['content_id']);
    }

    type setViewMode  = iState.Value['viewMode'];
    type setSelectedLabel = Project.Label.Item;
    type setPhotoNewMarkups = iState.Value["photoMarkup"]["newMarkups"];
    type deletePhotoNewMarkup = Photo.Frames.Markup["id"]
    type deleteOldMarkups = Photo.Frames.Markup["id"]
    type sendPhotoMarkups = {
        frames: {
            content_id: string;
            frame_id: string;
            new_markups: Omit<Markup, "confidence">[];
            deleted_markups: string[];
        }[],
        onSuccess?: () => void
    }
}

export type PageState = PageStateGeneric<{
    [Slice.name]: ReturnType<typeof Slice.reducer>
}>