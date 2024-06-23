import {call, put, takeLatest} from "typed-redux-saga";
import {PageActions} from '../Redux/Store';
import {iActions, iState} from '../Redux/types';
import Api from '@root/Api';
import {PayloadAction} from "@reduxjs/toolkit";

import {Frames} from "@root/Types/Video";
import { message } from "antd";


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

const getContentIds = function*(action: PayloadAction<iActions.getContentIds>) {
    try {
        const {data} = yield* call(Api.Projects.getContentIds, action.payload);
        yield* put(PageActions._getContentIdsSuccess(data.data));
    } catch (ex) {
        yield* put(PageActions._getContentIdsError())
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

const changeContentStatus = function*(action: PayloadAction<iActions.changeContentStatus>) {
    try {
        const {data} = yield* call(Api.Projects.changeContentStatus, action.payload);
        yield* put(PageActions._changeContentStatusSuccess(data.data));
        yield* put(PageActions.getContentInfo({content_id: action.payload.content_id}))
        action.payload.onSuccess && action.payload.onSuccess();
        
    } catch (ex) {
        yield* put(PageActions._changeContentStatusError())
    }
}

const sendPhotoMarkups = function*(action: PayloadAction<iActions.sendPhotoMarkups>) {
    try {
        yield* call(Api.Projects.sendPhotoMarkup, action.payload.frames);
        message.success("Данные для дообучения модели отправлены")
        console.log('success')
        action.payload.onSuccess && action.payload.onSuccess();
        
    } catch (ex) {
        message.error("Произошла ошибка при отправке данных о доразметке");
    }
}

const downloadResult = function* (action: PayloadAction<iActions.downloadResult>) {
    const {payload} = action;

    try {
        const response = yield* call(Api.Projects.downloadResult, [payload.content_id]);
        const data: BlobPart = response.data as unknown as BlobPart;
        if (!data) throw new Error("Ошибка скачивания документа");
        const blob = new Blob([data]);
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        const filename = "Result.txt";
        link.setAttribute("download", decodeURIComponent(filename));
        document.body.appendChild(link);
        link.click();
    } catch (error) {
        message.error("Ошибка скачивания документа");
    }
};


export default function* () {
    yield* takeLatest(PageActions.getContentInfo, getContentInfo);
    yield* takeLatest(PageActions.getLabels, getLabels);
    yield* takeLatest(PageActions.getContentIds, getContentIds);
    yield* takeLatest(PageActions.changeContentStatus, changeContentStatus);
    yield* takeLatest(PageActions.downloadResult, downloadResult);
    yield* takeLatest(PageActions.sendPhotoMarkups, sendPhotoMarkups);
}