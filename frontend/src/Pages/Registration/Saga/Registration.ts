import {call, takeLatest, put} from 'typed-redux-saga';
import {PageActions} from '../Redux/Store';
import Api from '@api'; 
import {PayloadAction} from '@reduxjs/toolkit';
import {iActions} from '../Redux/types';
import {getErrorMessage} from '@root/Utils/Request/getErrorMessage';
import {message} from 'antd';
import {LoginSaga} from '@root/Saga/User/Login';

const registration = function* (action: PayloadAction<iActions.registration>) {
    const {payload} = action;
    try { 
        const response = yield* call(Api.User.registration, action.payload);
        yield* call(LoginSaga, {
            username: payload.email,
            password: payload.password
        })
        const {data} = response;
        yield* put(PageActions._registrationSuccess(data.data))

    } catch (ex) {
        const msg = getErrorMessage(ex)
        yield* put(PageActions._registrationError(msg));
        message.error(msg)
    }
}

export default function*() {
    yield* takeLatest(PageActions.registration, registration)
}