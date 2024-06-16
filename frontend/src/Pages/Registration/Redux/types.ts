import {RequestFullState} from "@root/Utils/Redux/RequestState/types";
import {PageStateGeneric} from '@root/Redux/store';
import {Slice} from './Store';
import {Api} from '@root/Api/User/types';


export declare namespace iState {
    type Value = {
       registration: RequestFullState<Api.oRegistration>
    }
}


export declare namespace iActions {
    type registration = Api.iRegistration;
    type _registrationSuccess = Api.oRegistration;
    type _registrationError = string;
}

export type PageState = PageStateGeneric<{
    [Slice.name]: ReturnType<typeof Slice.reducer>
}>