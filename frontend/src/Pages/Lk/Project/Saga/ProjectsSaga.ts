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

const deleteProject = function*(action: PayloadAction<iActions.deleteProject>) {
    const {project_id, onError, onSuccess} = action.payload
    try {
        yield* call(Api.Projects.deleteProject, project_id)
        onSuccess && onSuccess();
    } catch (ex) {
        onError && onError();
    }
}


const uploadContent = function*(action: PayloadAction<iActions.uploadContent>) {
    const {params, onError, onSuccess} = action.payload
    try {
        const {data} = yield* call(Api.Projects.uploadContent, params)
        yield* put(PageActions.getProjectContent({project_id: params.project_id}));
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
    yield* takeLatest(PageActions.deleteProject, deleteProject);
    yield* takeLatest(PageActions.uploadContent, uploadContent);
    yield* takeLatest(PageActions.getProjectContent, getProjectContent);
}