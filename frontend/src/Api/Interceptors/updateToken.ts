import {AxiosInstance, isAxiosError, AxiosError} from 'axios';
import CS from '@root/Storages/Cookie';
import Actions from '@root/Redux/actions';
import store from '@root/Redux/store';


type AxiosErrorExtended = AxiosError & {
    retry?: boolean;
}
const isAxiosErrorExtended = (err: unknown):err is AxiosErrorExtended => isAxiosError(err) 

export const updateToken = (error: unknown, axiosInstance: AxiosInstance) => {
    const refresh = CS.token.getRefresh();
    if (!isAxiosErrorExtended(error)) return;
    if (error.retry) return Promise.reject(error);
    if (!error.response) return;
    if (error.response.status === 401) {
        if (!refresh) {
            return Promise.reject(error);
        }
    } else {
        return Promise.reject(error);
    }

    error.retry = true;
    return new Promise((resolve, reject) => {
        store.dispatch(Actions.User.getToken({
            refreshToken: refresh.token,
            onSuccess: () => {
                if (error.config) resolve(axiosInstance(error.config))
                else reject()
            },
            onError: () => {
                reject()
            }
        }))
    })
};