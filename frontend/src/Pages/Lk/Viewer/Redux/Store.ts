import {getFullState, requestStart, requestSuccess, requestError, getShortState} from '@root/Utils/Redux/RequestState/getRequestState';
import {createSlice, PayloadAction} from '@reduxjs/toolkit';
import {iState, iActions} from './types';

const initialState: iState.Value = {
    content: getFullState(),
    labels: getFullState(),
    playInterval: null,
    videoStatus: getShortState(),
    content_ids: getFullState(),
    viewMode: "result",
    selectedLabel: null,
    photoMarkup: {
        newMarkups: [],
        changedMarkups: [],
    },
    videoMarkup: [],
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

        setViewMode:  (state, action: PayloadAction<iActions.setViewMode>)  => {
            state.viewMode = action.payload;
        },
        setSelectedLabel:  (state, action: PayloadAction<iActions.setSelectedLabel>)  => {
            state.selectedLabel = action.payload;
        },
        eraseSelectedLabel:  (state)  => {
            state.selectedLabel = initialState.selectedLabel;
        },
        setPhotoNewMarkups:  (state, action: PayloadAction<iActions.setPhotoNewMarkups>)  =>  {
            state.photoMarkup.newMarkups  = action.payload;
        },
        deletePhotoNewMarkup: (state, action: PayloadAction<iActions.deletePhotoNewMarkup>) => {
            state.photoMarkup.newMarkups = state.photoMarkup.newMarkups.filter(markup => markup.id !== action.payload);
        },
        erasePhotoMarkup: (state)  =>  {
            state.photoMarkup = initialState.photoMarkup;
        },
        deleteOldMarkups: (state, action: PayloadAction<iActions.deleteOldMarkups>) => {
            state.photoMarkup.changedMarkups.push(action.payload);
        },
        sendPhotoMarkups: (state, action: PayloadAction<iActions.sendPhotoMarkups>) => state,
        addVideoNewMarkup: (state, action: PayloadAction<iActions.addVideoNewMarkup>)   => {
            const existFrame = state.videoMarkup.find((item) => item.frame_id = action.payload.frame_id);
            if (existFrame) {
                existFrame.new_markups.push(action.payload.new_markup)
            } else {
                state.videoMarkup.push({
                    frame_id: action.payload.frame_id,
                    content_id: action.payload.content_id,
                    new_markups: [action.payload.new_markup],
                    deleted_markups: [],
                })
            }
        }
    }   
});
export const PageActions = Slice.actions;
