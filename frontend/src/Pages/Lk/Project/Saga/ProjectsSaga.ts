import {call, put, takeLatest} from "typed-redux-saga";
import {PageActions} from '../Redux/Store';
import {iActions} from '../Redux/types';
import Api from '@root/Api';
import {PayloadAction} from "@reduxjs/toolkit";


const getProject = function*(action: PayloadAction<iActions.getProject>) {
    try {
        const {data} = yield* call(Api.Projects.getProject, action.payload)
        yield* put(PageActions._getProjectSuccess(data.data));

    } catch (ex) {
        yield* put(PageActions._getProjectError())
    }
}

const getApartments = function*(action: PayloadAction<iActions.getApartments>) {
    try {
        const {data} = yield* call(Api.Projects.getApartments, action.payload)
        yield* put(PageActions._getApartmentsSuccess(data.data));
    } catch (ex) {
        yield* put(PageActions._getApartmentError())
    }
}


const getProjectStats = function* (action: PayloadAction<iActions.getProjectStats>) {
    try {
        const {data} = yield* call(Api.Projects.getProjectStats, action.payload)
        yield* put(PageActions._getProjectStatsSuccess(data.data));
    } catch (ex) {
        yield* put(PageActions._getProjectStatsError());
    }
}


const getProjectFullStats = function* (action: PayloadAction<iActions.getFullStats>) {
    try {
        const {data} = yield* call(Api.Projects.getProjectFullStats, action.payload)
        yield* put(PageActions._getFullStatsSuccess(data.data));
    } catch (ex) {
        yield* put(PageActions._getFullStatsError());
    }
}

const uploadContent = function*(action: PayloadAction<iActions.uploadContent>) {
    const {params, onError, onSuccess} = action.payload
    try {
        const {data} = yield* call(Api.Projects.uploadContent, params)
        yield* put(PageActions._uploadContentError(data.data))
        onSuccess && onSuccess();
        
    } catch (ex) {
        yield* put(PageActions._uploadContentError())
        onError && onError();
    }
}

const getProjectContent = function*(action: PayloadAction<iActions.getProjectContent>) {
    try {
        const {data}  = yield* call(Api.Projects.getProjectContent, action.payload)
        yield* put(PageActions._getProjectContentSuccess(data.data));
    } catch (ex) {
        yield* put(PageActions._getProjectContentError())
    }
}

export default function* () {
    yield* takeLatest(PageActions.getProject, getProject);
    yield* takeLatest(PageActions.getApartments, getApartments);
    yield* takeLatest(PageActions.getProjectStats, getProjectStats);
    yield* takeLatest(PageActions.uploadContent, uploadContent);
    yield* takeLatest(PageActions.getFullStats, getProjectFullStats);
    yield* takeLatest(PageActions.getProjectContent, getProjectContent);
}