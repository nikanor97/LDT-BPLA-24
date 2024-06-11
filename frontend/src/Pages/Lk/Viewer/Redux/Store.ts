import {getFullState, requestStart, requestSuccess, requestError, getShortState} from '@root/Utils/Redux/RequestState/getRequestState';
import {createSlice, PayloadAction} from '@reduxjs/toolkit';
import {iState, iActions} from './types';

const initialState: iState.Value = {
    apartment: getFullState(),
    videos: getFullState(),
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

        getVideos: (state, action: PayloadAction<iActions.getVideos>) => 
            requestStart(state.videos),
        _getVideosSuccess: (state, action: PayloadAction<iActions._getVideosSuccess>) =>
            requestSuccess(state.videos, action.payload),
        _getVideosError: (state) => 
            requestError(state.videos),
        updateVideoMeta: (state, action:PayloadAction<iActions.updateVideoMeta>) => {
            if (!state.videos.data?.video) return state;
            state.videos.data.video = {
                ...state.videos.data.video,
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
            if (state.videos.data?.video) {
                state.videos.data.video = action.payload
            }
        },
        
        _changeVideoStatusError: (state) => 
            requestError(state.videoStatus),

    }   
});
export const PageActions = Slice.actions;
