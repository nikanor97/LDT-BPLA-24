import {getFullState, requestStart, requestSuccess, requestError} from '@root/Utils/Redux/RequestState/getRequestState';
import {createSlice, PayloadAction} from '@reduxjs/toolkit';
import {iState, iActions} from './types';

const initialState: iState.Value = {
    upload: getFullState(),
    getProject: getFullState(),
    apartments: getFullState(),
    content: getFullState(),
    uploadDrawer: {
        visible: false
    },
    uploadContent: getFullState(),
    statistics: {
        request: getFullState(),
        fullRequest: getFullState(),
        filters: {
            mode: 'floor',
            detalisation: 'mop'
        }
    }
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

        getProjectStats: (state, action: PayloadAction<iActions.getProjectStats>) =>
            requestStart(state.statistics.request),
        _getProjectStatsSuccess: (state, action: PayloadAction<iActions._getProjectStatsSuccess>) =>  
            requestSuccess(state.statistics.request, action.payload),
        _getProjectStatsError: (state) =>
            requestError(state.statistics.request),

        getApartments: (state, action: PayloadAction<iActions.getApartments>) =>
            requestStart(state.apartments),
        _getApartmentsSuccess: (state, action: PayloadAction<iActions._getApartmentsSuccess>) =>
            requestSuccess(state.apartments, action.payload),
        _getApartmentError: (state) =>
            requestError(state.apartments),

        getFullStats: (state, action: PayloadAction<iActions.getFullStats>) =>
            requestStart(state.statistics.fullRequest),
        _getFullStatsSuccess: (state, action: PayloadAction<iActions._getFullStatsSuccess>) =>
            requestSuccess(state.statistics.fullRequest, action.payload),
        _getFullStatsError: (state) =>
            requestError(state.statistics.fullRequest),


        setStatisticFilters: (state, action: PayloadAction<iActions.setStatisticFilters>) => {
            state.statistics.filters = action.payload;
        },

        getProjectContent: (state, action: PayloadAction<iActions.getProjectContent>) =>
            requestStart(state.content),
        _getProjectContentSuccess: (state, action: PayloadAction<iActions._getProjectContentSuccess>) =>
            requestSuccess(state.content, action.payload),
        _getProjectContentError: (state)  =>
            requestError(state.content),
    }   
});
export const PageActions = Slice.actions;
