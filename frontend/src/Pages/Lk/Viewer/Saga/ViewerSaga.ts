import {call, put, takeLatest} from "typed-redux-saga";
import {PageActions} from '../Redux/Store';
import {iActions, iState} from '../Redux/types';
import Api from '@root/Api';
import {PayloadAction} from "@reduxjs/toolkit";

import {Frames} from "@root/Types/Video";



const getApartment = function*(action: PayloadAction<iActions.getApartment>) {
    try {
        const {data} = yield* call(Api.Projects.getApartment, action.payload)
        yield* put(PageActions._getApartmentSuccess(data.data));
    } catch (ex) {
        yield* put(PageActions._getApartmentError())
    }
}

const getLabels = function*(action: PayloadAction<iActions.getLabels>) {
    try {
        const {data} = yield* call(Api.Projects.getLabels, action.payload);
        const results:iState.Labels = {};
        data.data.forEach((item) => {
            results[item.id] = item;
        })
        yield* put(PageActions._getLabelsSuccess(results));
    } catch (ex) {
        yield* put(PageActions._getLabelsError())
    }
}

const getVideos = function*(action: PayloadAction<iActions.getVideos>) {
    try {
        const videos = yield* call(Api.Projects.getApartmentVideos, action.payload)
        const video = videos.data.data[videos.data.data.length - 1];
        if (!video) {
            yield* put(PageActions._getVideosSuccess({
                frames: null,
                video: null
            }));
        }
        const frames = yield* call(Api.Projects.getVideoFrames, {
            video_id: video.id
        })
        const framesObject: {[index: number]: Frames.MarkupedItem} = {};
        frames.data.data.forEach((frame) => {
            framesObject[frame.frame_offset] = frame;
        })
        yield* put(PageActions._getVideosSuccess({
            frames: framesObject,
            video
        }));
    } catch (ex) {
        yield* put(PageActions._getVideosError())
    }
}

const changeVideoStatus = function*(action: PayloadAction<iActions.changeVideoStatus>) {
    try {
        const {data} = yield* call(Api.Projects.changeVideoStatus, action.payload)
        yield* put(PageActions._changeVideoStatusSuccess(data.data))
        yield* put(PageActions.getApartment({apartId: data.data.apartment_id}))
        
    } catch (ex) {
        yield* put(PageActions._changeVideoStatusError())
    }
}


export default function* () {
    yield* takeLatest(PageActions.getApartment, getApartment);
    yield* takeLatest(PageActions.getVideos, getVideos);
    yield* takeLatest(PageActions.getLabels, getLabels);
    yield* takeLatest(PageActions.changeVideoStatus, changeVideoStatus);
}