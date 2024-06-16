import {RequestFullState} from "@root/Utils/Redux/RequestState/types";
import {PageStateGeneric} from '@root/Redux/store';
import {Slice} from './Store';
import {Api} from '@root/Api/Projects/types';
import {Video, Photo} from '@root/Types';

export declare namespace iState {
    type Value = {
        upload: RequestFullState<null>
        getProject: RequestFullState<Api.oGetProject>;
        uploadDrawer: {
            visible: boolean;
        }
        uploadContent: RequestFullState<Api.oUploadContent>;
        content: RequestFullState<Array<Video.Item | Photo.Item> | null>
    }
}


export declare namespace iActions {
    type getProject = Api.iGetProject;
    type _getProectSuccess = Api.oGetProject;
    type deleteProject = {
        project_id: string,
        onSuccess?:  ()  => void;
        onError?:  ()  => void;
    };

    type getProjectStats = Api.iGetProjectStats;

    type uploadContent =  {
        params: Api.iUploadContent;
        onSuccess?: () => any; 
        onError?: () => any; 
    };
    type _uploadContentSuccess = Api.oUploadContent;

    type getProjectContent  = Api.iGetProjectContent;
    type _getProjectContentSuccess = Api.oGetProjectContent;
}

export type PageState = PageStateGeneric<{
    [Slice.name]: ReturnType<typeof Slice.reducer>
}>