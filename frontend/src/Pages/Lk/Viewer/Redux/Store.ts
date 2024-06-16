import {getFullState, requestStart, requestSuccess, requestError, getShortState} from '@root/Utils/Redux/RequestState/getRequestState';
import {createSlice, PayloadAction} from '@reduxjs/toolkit';
import {iState, iActions} from './types';

const initialState: iState.Value = {
    content: getFullState(),
    labels: getFullState(),
    playInterval: null,
    videoStatus: getShortState(),
    content_ids: getFullState(),
};


export const Slice = createSlice({
    name: 'LkViewer',
    initialState,
    reducers: {

        getContentInfo: (state, action: PayloadAction<iActions.getContentInfo>) => 
            requestStart(state.content),
        _getContentInfoSuccess: (state, action: PayloadAction<iActions._getContentInfoSuccess>) =>
            requestSuccess(state.content, action.payload),
        _getContentInfoError: (state) => 
            requestError(state.content),
        updateVideoMeta: (state, action:PayloadAction<iActions.updateVideoMeta>) => {
            if (!state.content.data?.info) return state;
            state.content.data.info = {
                ...state.content.data.info,
                ...action.payload
            }
        },

        getLabels: (state, action: PayloadAction<iActions.getLabels>) => 
            requestStart(state.labels),
        _getLabelsSuccess: (state, action: PayloadAction<iActions._getLabelsSuccess>) =>
            requestSuccess(state.labels, action.payload),
        _getLabelsError: (state) => 
            requestError(state.labels),

        getContentIds: (state, action: PayloadAction<iActions.getContentIds>) => 
            requestStart(state.content_ids),
        _getContentIdsSuccess: (state, action: PayloadAction<iActions._getContentIdsSuccess>) =>
            requestSuccess(state.content_ids, action.payload),
        _getContentIdsError: (state) => 
            requestError(state.content_ids),

        setPlayInterval: (state, action: PayloadAction<iActions.setPlayInterval>) => {
            state.playInterval = action.payload;
        },

        changeContentStatus: (state, action: PayloadAction<iActions.changeContentStatus>) =>    
            requestStart(state.videoStatus),
        _changeContentStatusSuccess: (state, action: PayloadAction<iActions._changeContenttatusSuccess>) => {
            requestSuccess(state.videoStatus)
            if (state.content.data?.info) {
                state.content.data.info = action.payload
            }
        },
        
        _changeContentStatusError: (state) => 
            requestError(state.videoStatus),

        downloadResult: (state, action: PayloadAction<iActions.downloadResult>) => state,
    }   
});
export const PageActions = Slice.actions;
