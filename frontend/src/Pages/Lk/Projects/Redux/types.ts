import {RequestFullState} from "@root/Utils/Redux/RequestState/types";
import {PageStateGeneric} from '@root/Redux/store';
import {Slice} from './Store';
import {Api} from '@root/Api/Projects/types';
import {Api as UserApi} from '@root/Api/User/types';
import { RcFile } from "antd/es/upload";


export declare namespace iState {
    type Value = {
        createDrawer: {
            visible: boolean;
        }
        projects: RequestFullState<Api.oGetMyProjects>;
        create: RequestFullState<null>;
        tags: RequestFullState<Api.oGetTags>;
        statistics: RequestFullState<Api.oGetProjectsStats>;
    }
}

export declare namespace iActions {
    type _getProjectsSuccess = Api.oGetMyProjects;
    
    type createProject = {
        params: Api.iCreateProject;
        onSuccess?: () => any;
        onError?: () => any;
    }
    type _createProjectSuccess = Api.oCreateProject;

    type _getTagsSuccess = Api.oGetTags;
    type _getUsersSuccess = UserApi.oGetUsers;

    type _getProjectStatsSuccess = Api.oGetProjectsStats;
}

export type PageState = PageStateGeneric<{
    [Slice.name]: ReturnType<typeof Slice.reducer>
}>