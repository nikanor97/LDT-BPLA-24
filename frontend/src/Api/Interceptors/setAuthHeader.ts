import CS from '@root/Storages/Cookie';
import {InternalAxiosRequestConfig} from 'axios';

export const setAuthHeader = (config: InternalAxiosRequestConfig) => {
    const access = CS.token.getAccess();
    if (access?.token) {
        config.headers.Authorization = `Bearer ${access.token}`;
    } else {
        delete config.headers.Authorization;
    }
    return config;
};