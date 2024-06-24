import {getFullState, requestStart, requestSuccess, requestError} from '@root/Utils/Redux/RequestState/getRequestState';
import {createSlice, PayloadAction} from '@reduxjs/toolkit';
import {iState, iActions} from './types';

const initialState: iState.Value = {
    createDrawer: {
        visible: false
    },
    projects: getFullState(),
    create: getFullState(),
    tags: getFullState(),
    statistics: getFullState()
};


export const Slice = createSlice({
    name: 'LkProjects',
    initialState,
    reducers: {
        getProjects: (state) => 
            requestStart(state.projects),
        _getProjectsSuccess: (state, action: PayloadAction<iActions._getProjectsSuccess>) => 
            requestSuccess(state.projects, action.payload),
        _getProjectsError: (state) => 
            requestError(state.projects),
        
        openCreateProject: (state) => {
            state.createDrawer.visible = true
        },
        closeCreateProject: (state) => {
            state.createDrawer.visible = false
        },

        getTags: (state) => 
            requestStart(state.tags),
        _getTagsSuccess: (state, action: PayloadAction<iActions._getTagsSuccess>) => 
            requestSuccess(state.tags, action.payload),
        _getTagsError: (state) => 
            requestError(state.tags),
            

        createProject: (state, action: PayloadAction<iActions.createProject>) =>
            requestStart(state.create),
        _createProjectSuccess: (state, action: PayloadAction<iActions._createProjectSuccess>) => 
            requestSuccess(state.create, action.payload),
        _createProjectError: (state) => 
            requestError(state.create),

        getProjectsStats: (state) =>
            requestStart(state.statistics),
        _getProjectsStatsSuccess: (state, action: PayloadAction<iActions._getProjectsStatsSuccess>) => 
            requestSuccess(state.statistics, action.payload),
        _getProjectsStatsError: (state) => 
            requestSuccess(state.statistics),    
    }   
});
export const PageActions = Slice.actions;
