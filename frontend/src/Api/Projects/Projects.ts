import axios from '../Request';
import paths from './paths';
import {Api} from './types';
import qs from 'qs';
import {omit} from 'lodash';

export default {
    getProjects: (userId: Api.iGetProjects) => {
        return axios.get<Api.oGetProjects>(`${paths.getProjects}`, {
            params: {
                user_id: userId
            }
        })
    },
    getProject: (projectId: Api.iGetProject) => {
        return axios.get<Api.oGetProject>(paths.getProject, {
            params: {
                project_id: projectId
            }
        })  
    },
    getApartments: (projectId: Api.iGetApartments) => {
        return axios.get<Api.oGetApartments>(paths.getApartments, {
            params: {
                project_id: projectId
            }
        })  
    },
    getApartment: (params: Api.iGetApartment) => {
        return axios.get<Api.oGetApartment>(paths.getApartment, {
            params: {
                apartment_id: params.apartId
            }
        })
    },
    createProject: (params: Api.iCreateProject) => {
        return axios.post<Api.oCreateProject>(paths.createProject, {
            ...params,
            status: "created",
            is_deleted: false
        })
    },
    getProjectVideos: (params: Api.iGetProjectVideos) => {
        return axios.get(paths.getProjectVideos, {
            params
        })
    },
    getTags: () =>
        axios.get<Api.oGetTags>(paths.getTags),
    getApartmentVideos: (params: Api.iGetApartmentVideos) =>
        axios.get<Api.oGetApartmentVideos>(paths.getApartmentVideos, {params}),

    getProjectContent: (params: Api.iGetProjectContent) =>
        axios.get<Api.oGetProjectContent>(paths.getProjectContent, {params}),

    getVideoFrames: (params: Api.iGetVideoFrames) => 
        axios.get<Api.oGetVideoFrames>(paths.getVideoFrames, {params}),
    getLabels: (params: Api.iGetLabels) => 
        axios.get<Api.oGetLabels>(paths.getLabels, {params}),
    uploadContent: (params: Api.iUploadContent) => {
        const fileData = new FormData();
        const search = qs.stringify(omit(params, ['document']), {addQueryPrefix: true})
        params.document.forEach((item) => {
            fileData.append("file", (item));
        });
        return axios.post<Api.oUploadContent>(`${paths.uploadProjectContent}${search}`, fileData, {
            headers: {
                "Content-Type": 'multipart/form-data'
            }
        })
    },
    getProjectsStats: () =>
        axios.get<Api.oGetProjectsStats>(paths.getStats),
    getMyProjects: () =>
        axios.get<Api.oGetMyProjects>(paths.getMyProjects),
    getProjectStats: (params: Api.iGetProjectStats) => 
        axios.get<Api.oGetProjectStats>(paths.getProjectStats, {params}),
    getProjectFullStats: (params: Api.iGetProjectFullStats) =>
        axios.get<Api.oGetProjectFullStats>(paths.getProjectFullStats, {params}),

    changeVideoStatus: (params: Api.iChangeVideoStatus) => 
        axios.post<Api.oChangeVideoStatus>(`${paths.changeVideoStatus}${qs.stringify(params, {addQueryPrefix: true})}`),
}