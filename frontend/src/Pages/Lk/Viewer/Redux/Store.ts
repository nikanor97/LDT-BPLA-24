import {getFullState, requestStart, requestSuccess, requestError, getShortState} from '@root/Utils/Redux/RequestState/getRequestState';
import {createSlice, PayloadAction} from '@reduxjs/toolkit';
import {iState, iActions} from './types';

const initialState: iState.Value = {
    apartment: getFullState(),
    content: getFullState(),
    labels: getFullState(),
    playInterval: null,
    videoStatus: getShortState(),
};


export const Slice = createSlice({
    name: 'LkViewer',
    initialState,
    reducers: {
        getApartment: (state, action: PayloadAction<iActions.getApartment>) =>
            requestStart(state.apartment),
        _getApartmentSuccess: (state, action: PayloadAction<iActions._getApartmentSuccess>) =>
            requestSuccess(state.apartment, action.payload),
        _getApartmentError: (state) => 
            requestError(state.apartment),

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

        setPlayInterval: (state, action: PayloadAction<iActions.setPlayInterval>) => {
            state.playInterval = action.payload;
        },

        changeVideoStatus: (state, action: PayloadAction<iActions.changeVideoStatus>) =>    
            requestStart(state.videoStatus),
        _changeVideoStatusSuccess: (state, action: PayloadAction<iActions._changeVideoStatusSuccess>) => {
            requestSuccess(state.videoStatus)
            if (state.content.data?.info) {
                state.content.data.info = action.payload
            }
        },
        
        _changeVideoStatusError: (state) => 
            requestError(state.videoStatus),

    }   
});
export const PageActions = Slice.actions;
