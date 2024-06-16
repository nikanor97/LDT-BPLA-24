import {isAxiosError} from 'axios';
import {Api} from '@root/Types'


export const getErrorMessage = (ex: any) => {
    if (isAxiosError(ex)) {
        return 'Ошибка при получении ответа от сервера';
    }
    if (Api.Guard.isBadResponse(ex)) {
        return ex.data.error || 'Произошла ошибка при получении ответа от сервера'
    }
    return 'Произошла системная ошибка';
}