import Axios from 'axios';
import Qs from 'qs';
import {Api} from '@root/Types';
import {setAuthHeader} from './Interceptors/setAuthHeader';
import {updateToken} from './Interceptors/updateToken';


const axios = Axios.create({
    baseURL: '/api',
    paramsSerializer: (params) => Qs.stringify(params, {arrayFormat: 'repeat'})
});

axios.interceptors.response.use((response) => {
    if (Api.Guard.isBadResponse(response)) {
        return Promise.reject(response)
    }
    return response;
})

axios.interceptors.request.use(setAuthHeader);
axios.interceptors.response.use((response) => response, (error) => updateToken(error, axios))



export default {
    ...axios,
    get: function<T> (...args: Parameters<typeof axios.get>) {
        return axios.get<Api.SuccessResponse<T>>(...args)
    },
    post: function<T> (...args: Parameters<typeof axios.post>) {
        return axios.post<Api.SuccessResponse<T>>(...args)
    },
    delete: function<T> (...args: Parameters<typeof axios.get>) {
        return axios.delete<Api.SuccessResponse<T>>(...args)
    },
}




