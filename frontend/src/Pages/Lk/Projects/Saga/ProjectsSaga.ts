import { call, put, takeLatest } from "typed-redux-saga";
import {PageActions} from '../Redux/Store';
import {iActions} from '../Redux/types';
import Api from '@root/Api';
import { PayloadAction } from "@reduxjs/toolkit";


const getMyProjects = function*() {
    try {
        const {data} = yield* call(Api.Projects.getMyProjects)
        yield* put(PageActions._getProjectsSuccess(data.data));
    } catch (ex) {
        yield* put(PageActions._getProjectsError())
    }
}

const createProject = function*(action: PayloadAction<iActions.createProject>) {
    const {params, onSuccess, onError} = action.payload;
    try {
        const {data} = yield* call(Api.Projects.createProject, params)
        yield* put(PageActions._createProjectSuccess(data.data));
        onSuccess && onSuccess();
    } catch (ex) {
        yield* put(PageActions._createProjectError())
        onError && onError();
    }
}

const getTags = function*() {
    try {
        const {data} = yield* call(Api.Projects.getTags)
        yield* put(PageActions._getTagsSuccess(data.data));
    } catch (ex) {
        yield* put(PageActions._getTagsError());
    }
}

const getProjectsStats = function*() {
    try {
        const {data} = yield* call(Api.Projects.getProjectsStats)
        yield* put(PageActions._getProjectStatsSuccess(data.data));
    } catch (ex) {
        yield* put(PageActions._getProjectStatsError());
    }
}




export default function* () {
    yield* takeLatest(PageActions.getProjects, getMyProjects)
    yield* takeLatest(PageActions.createProject, createProject)
    yield* takeLatest(PageActions.getTags, getTags)
    yield* takeLatest(PageActions.getProjectStats, getProjectsStats)
}