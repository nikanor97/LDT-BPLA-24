import {RequestFullState} from "@root/Utils/Redux/RequestState/types";
import {PageStateGeneric} from '@root/Redux/store';
import {Slice} from './Store';
import {Api} from '@root/Api/Projects/types';
import {Project, Video, Photo} from '@root/Types';

export declare namespace iState {
    type Value = {
        upload: RequestFullState<null>
        getProject: RequestFullState<Api.oGetProject>;
        apartments: RequestFullState<Api.oGetApartments>
        uploadDrawer: {
            visible: boolean;
        }
        uploadContent: RequestFullState<Api.oUploadContent>;
        statistics: {
            request: RequestFullState<Api.oGetProjectStats>;
            fullRequest: RequestFullState<Api.oGetProjectFullStats>;
            filters: Project.Statistics.Filters;
        }
        content: RequestFullState<Array<Video.Item | Photo.Item> | null>
    }
}


export declare namespace iActions {
    type getProject = Api.iGetProject;
    type _getProectSuccess = Api.oGetProject;

    type getProjectStats = Api.iGetProjectStats;
    type _getProjectStatsSuccess = Api.oGetProjectStats;

    type getApartments = Api.iGetApartments;
    type _getApartmentsSuccess = Api.oGetApartments;
    type setStatisticFilters = Project.Statistics.Filters;

    type getFullStats = Api.iGetProjectFullStats;
    type _getFullStatsSuccess = Api.oGetProjectFullStats;

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