import Api from '@root/Api';
import {Api as iApi} from '@root/Api/User/types';
import {call, put, takeLatest} from 'typed-redux-saga';
import Actions from '@root/Redux/actions';
import CS from '@root/Storages/Cookie';
import {User} from '@root/Types';
import {iActions} from '@root/Redux/User/types';
import {PayloadAction} from '@reduxjs/toolkit';


export const updateTokens = (data: User.Token) => {
    CS.token.setAccess(data.access_token, data.access_expires_at);
    CS.token.setRefresh(data.refresh_token, data.refresh_expires_at)
}

export const LoginSaga = function* (params: iApi.iLogin) {
    const response = yield* call(Api.User.login, params);
    const {data} = response.data;
    yield* put(Actions.User._getTokenSuccess(data));
    yield* call(updateTokens, data)
    return data;
}


const getToken = function*(action: PayloadAction<iActions.getToken>) {
    const {payload} = action;
    try {
        const {data} = yield* call(Api.User.refreshToken, payload.refreshToken);
        yield* call(updateTokens, data.data)
        yield* put(Actions.User._getTokenSuccess(data.data))
        payload.onSuccess && payload.onSuccess();
    } catch (ex) {
        yield* put(Actions.User._getTokenError())
        payload.onError && payload.onError();
    }
}

export default function*() {
    yield* takeLatest(Actions.User.getToken, getToken)
}