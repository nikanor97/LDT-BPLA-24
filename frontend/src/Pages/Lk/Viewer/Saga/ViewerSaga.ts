import {call, put, takeLatest} from "typed-redux-saga";
import {PageActions} from '../Redux/Store';
import {iActions, iState} from '../Redux/types';
import Api from '@root/Api';
import {PayloadAction} from "@reduxjs/toolkit";

import {Frames} from "@root/Types/Video";


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

const getContentInfo = function*(action: PayloadAction<iActions.getContentInfo>) {
    try {
        const infoData = yield* call(Api.Projects.getContentInfo, action.payload)
        const info = infoData.data.data;
        if (!info) {
            yield* put(PageActions._getContentInfoSuccess({
                frames: null,
                info: null
            }));
        }
        const frames = yield* call(Api.Projects.getContentFrames, {
            content_id: info.content_id
        })
        const framesObject: {[index: number]: Frames.MarkupedItem} = {};
        frames.data.data.forEach((frame) => {
            framesObject[frame.frame_offset] = frame;
        })
        yield* put(PageActions._getContentInfoSuccess({
            frames: framesObject,
            info
        }));
    } catch (ex) {
        yield* put(PageActions._getContentInfoError())
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
    yield* takeLatest(PageActions.getContentInfo, getContentInfo);
    yield* takeLatest(PageActions.getLabels, getLabels);
    yield* takeLatest(PageActions.changeVideoStatus, changeVideoStatus);
}