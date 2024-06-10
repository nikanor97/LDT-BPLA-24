import {RequestFullState, RequestShortState} from "@root/Utils/Redux/RequestState/types";
import {PageStateGeneric} from '@root/Redux/store';
import {Slice} from './Store';
import {Api} from '@root/Api/Projects/types';
import {Apartment, Video, Project} from '@root/Types';


export declare namespace iState {
    type VideosState = {
        video: Video.Item | null;
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
        apartment: RequestFullState<Apartment.Item>
        videos: RequestFullState<VideosState>;
        labels: RequestFullState<Labels>;
        uploadDrawer: {
            visible: boolean;
        }
        uploadVideo: RequestFullState<Api.oUploadContent>;
        apartmentDrawer: {
            visible: boolean;
            imageIndex: number;
        }
        playInterval: PlayInterval | null;
        videoStatus: RequestShortState;
        sidebarScores: RequestFullState<Api.oGetApartmentScores>
        
    }
}


export declare namespace iActions {
    type getApartment = Api.iGetApartment;
    type _getApartmentSuccess = Api.oGetApartment;

    type getVideos = Api.iGetApartmentVideos;
    type _getVideosSuccess = iState.VideosState;

    type getLabels = Api.iGetLabels;
    type _getLabelsSuccess = iState.Labels
    type updateVideoMeta = Partial<Video.Item>

    type uploadVideo =  {
        params: Api.iUploadContent;
        onSuccess?: () => any; 
        onError?: () => any; 
    };
    type _uploadVideoSuccess = Api.oUploadContent;
    type setPlayInterval = iState.PlayInterval | null;
    type changeVideoStatus = Api.iChangeVideoStatus;
    type _changeVideoStatusSuccess = Api.oChangeVideoStatus;
    type setImageIndex = number;

    type getApartmentScores = Api.iGetApartmentScores;
    type _getApartmentScoresSuccess = Api.oGetApartmentScores;
}

export type PageState = PageStateGeneric<{
    [Slice.name]: ReturnType<typeof Slice.reducer>
}>