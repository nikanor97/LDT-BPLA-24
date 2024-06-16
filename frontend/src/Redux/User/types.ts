import {User} from '@root/Types';
import {RequestFullState} from '@root/Utils/Redux/RequestState/types';


export declare namespace iState {
    type Value = {
        Info: RequestFullState<User.Info>;
        Token: RequestFullState<User.Token>;
    }
}
export declare namespace iActions {
    type _getTokenSuccess = User.Token;
    type _getUserInfoSuccess = User.Info | null;
    type getToken = {
        refreshToken: string,
        onSuccess?: () => any;
        onError?: () => any;
    }
}