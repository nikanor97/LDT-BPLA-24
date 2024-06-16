import Actions from '@root/Redux/actions';
import {call, put, takeLatest} from 'typed-redux-saga';
import Api from '@root/Api';

const getUserInfo = function*() {
    try {
        const {data} = yield* call(Api.User.me)
        yield* put(Actions.User._getUserInfoSuccess(data.data));
    } catch (ex) {
        yield* put(Actions.User._getUserInfoSuccess(null))
    }
}

export default function*() {
    yield* takeLatest(Actions.User.getUserInfo, getUserInfo)
}