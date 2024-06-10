import axios from '../Request';
import paths from './paths';
import {Api} from './types';
import qs from 'qs';

export default {
    login: (params: Api.iLogin) => {
        return axios.post<Api.oLogin>(paths.login, params)
    },
    registration: (params: Api.iRegistration) => {
        return axios.post<Api.oRegistration>(paths.registration, params)
    },
    me: () => axios.get<Api.oMe>(paths.me),
    refreshToken: (params: Api.iRefreshToken) => {
        const search = qs.stringify({refresh_token: params}, {addQueryPrefix: true});
        return axios.post<Api.oRefreshToken>(`${paths.refreshToken}${search}`)
    },
    getUsers: () =>
        axios.get<Api.oGetUsers>(paths.getUsers)
}