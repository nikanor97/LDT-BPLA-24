import {getFullState, requestStart, requestSuccess, requestError, getShortState} from '@root/Utils/Redux/RequestState/getRequestState';
import {createSlice, PayloadAction} from '@reduxjs/toolkit';
import {iState, iActions} from './types';

const initialState: iState.Value = {
    apartment: getFullState(),
    videos: getFullState(),
    labels: getFullState(),
    uploadDrawer: {
        visible: false
    },
    apartmentDrawer: {
        visible: false,
        imageIndex: 0,
    },
    uploadVideo: getFullState(),
    playInterval: null,
    videoStatus: getShortState(),
    sidebarScores: getFullState()
    
};


export const Slice = createSlice({
    name: 'LkApartment',
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

        openUploadDrawer: (state) => {
            state.uploadDrawer.visible = true;
        },
        closeUploadDrawer: (state) => {
            state.uploadDrawer.visible = false;
        },
        openApartmentDrawer: (state) => {
            state.apartmentDrawer.visible = true;
        },
        closeApartmentDrawer: (state) => {
            state.apartmentDrawer.visible = false;
        },

        setPlayInterval: (state, action: PayloadAction<iActions.setPlayInterval>) => {
            state.playInterval = action.payload;
        },

        uploadVideo: (state, action: PayloadAction<iActions.uploadVideo>) => 
            requestStart(state.uploadVideo),
        _uploadVideoSuccess: (state, action: PayloadAction<iActions._uploadVideoSuccess>) =>
            requestSuccess(state.uploadVideo, action.payload),
        _uploadVideoError: (state) => 
            requestError(state.uploadVideo),

        changeVideoStatus: (state, action: PayloadAction<iActions.changeVideoStatus>) =>    
            requestStart(state.videoStatus),
        _changeVideoStatusSuccess: (state, action: PayloadAction<iActions._changeVideoStatusSuccess>) => {
            requestSuccess(state.videoStatus)
            if (state.videos.data?.video) {
                state.videos.data.video = action.payload
            }
        },

        getApartmentScores: (state, action: PayloadAction<iActions.getApartmentScores>) => 
            requestStart(state.sidebarScores),
        _getApartmentScoresSuccess: (state, action: PayloadAction<iActions._getApartmentScoresSuccess>) => 
            requestSuccess(state.sidebarScores, action.payload),
        _getApartmentScoresError: (state) =>
            requestError(state.sidebarScores),
        
        _changeVideoStatusError: (state) => 
            requestError(state.videoStatus),

        setImageIndex: (state, action: PayloadAction<iActions.setImageIndex>) => {
            state.apartmentDrawer.imageIndex = action.payload;
        }

    }   
});
export const PageActions = Slice.actions;
