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
    deleteProject: (projectId: Api.iDeleteProject) => {
        return axios.delete<Api.oDeleteProject>(paths.deleteProject, {
            params: {
                project_id: projectId
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
    getContentInfo: (params: Api.iGetContentInfo) =>
        axios.get<Api.oGetContentInfo>(paths.getContentInfo, {params}),

    getProjectContent: (params: Api.iGetProjectContent) =>
        axios.get<Api.oGetProjectContent>(paths.getProjectContent, {params}),

    getContentFrames: (params: Api.iGetContentFrames) => 
        axios.get<Api.oGetContentFrames>(paths.getContentFrames, {params}),
    getLabels: (params: Api.iGetLabels) => 
        axios.get<Api.oGetLabels>(paths.getLabels, {params}),
    uploadContent: (params: Api.iUploadContent) => {
        const fileData = new FormData();
        const search = qs.stringify(omit(params, ['document']), {addQueryPrefix: true})
        params.document.forEach((item) => {
            fileData.append("files", (item));
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
    changeContentStatus: (params: Api.iChangeContentStatus) => 
        axios.post<Api.oChangeContentStatus>(`${paths.changeContentStatus}${qs.stringify(params, {addQueryPrefix: true})}`),
}