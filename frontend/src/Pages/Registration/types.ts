import {Api} from '@root/Api/User/types';

export type FormData = Api.iRegistration & {
    passwordConfirm: string
};