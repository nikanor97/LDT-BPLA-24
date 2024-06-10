import {RequestFullState} from "@root/Utils/Redux/RequestState/types";
import {PageStateGeneric} from '@root/Redux/store';
import {Slice} from './Store';
import {Api} from '@root/Api/User/types';

export declare namespace iState {
    type Value = {
       login: RequestFullState<Api.oLogin>
    }
}

export declare namespace iActions {
    type login = Api.iLogin
    type _loginSuccess = Api.oLogin
    type _loginError = string;
}

export type PageState = PageStateGeneric<{
    [Slice.name]: ReturnType<typeof Slice.reducer>
}>