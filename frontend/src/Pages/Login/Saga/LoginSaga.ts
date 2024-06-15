import {call, takeLatest, put} from 'typed-redux-saga';
import {PageActions} from '../Redux/Store';
import {PayloadAction} from '@reduxjs/toolkit';
import {iActions} from '../Redux/types';
import {getErrorMessage} from '@root/Utils/Request/getErrorMessage';
import {message} from 'antd';
import {LoginSaga} from '@root/Saga/User/Login';

const login = function* (action: PayloadAction<iActions.login>) {
    try { 
        const data = yield* call(LoginSaga, action.payload)
        yield* put(PageActions._loginSuccess(data))
    } catch (ex) {
        const msg = getErrorMessage(ex)
        yield* put(PageActions._loginError(msg));
        message.error(msg);
    }
}

export default function*() {
    yield* takeLatest(PageActions.login, login)
}