import {getFullState, requestStart, requestSuccess, requestError} from '@root/Utils/Redux/RequestState/getRequestState';
import {createSlice, PayloadAction} from '@reduxjs/toolkit';
import {iState, iActions} from './types';

const initialState: iState.Value = {
    upload: getFullState(),
    getProject: getFullState(),
    content: getFullState(),
    uploadDrawer: {
        visible: false
    },
    uploadContent: getFullState(),
    selectedContent: []
};


export const Slice = createSlice({
    name: 'LkProject',
    initialState,
    reducers: {

        uploadDocument: (state) => 
            requestStart(state.upload),

        getProject: (state, action: PayloadAction<iActions.getProject>) => 
            requestStart(state.getProject),
        _getProjectSuccess: (state, action: PayloadAction<iActions._getProectSuccess>) =>
            requestSuccess(state.getProject, action.payload),
        _getProjectError: (state) =>
            requestError(state.getProject),
        deleteProject: (state, action: PayloadAction<iActions.deleteProject>) => 
            state,

        openUploadDrawer: (state) => {
            state.uploadDrawer.visible = true;
        },
        closeUploadDrawer: (state) => {
            state.uploadDrawer.visible = false;
        },

        uploadContent: (state, action: PayloadAction<iActions.uploadContent>) => 
            requestStart(state.uploadContent),
        _uploadContentSuccess: (state, action: PayloadAction<iActions._uploadContentSuccess>) =>
            requestSuccess(state.uploadContent, action.payload),
        _uploadContentError: (state) => 
            requestError(state.uploadContent),

        getProjectContent: (state, action: PayloadAction<iActions.getProjectContent>) =>
            requestStart(state.content),
        _getProjectContentSuccess: (state, action: PayloadAction<iActions._getProjectContentSuccess>) =>
            requestSuccess(state.content, action.payload),
        _getProjectContentError: (state)  =>
            requestError(state.content),
        stopGetProjectContent: (state) =>
            state,
        setSelectedContent: (state, action: PayloadAction<iActions.setSelectedContent>) => {
            state.selectedContent = action.payload;
        },
        eraseSelectedContent: (state)  =>  {
            state.selectedContent = initialState.selectedContent;
        },
        downloadResult: (state, action: PayloadAction<iActions.downloadResult>) => state,
    }   
});
export const PageActions = Slice.actions;
