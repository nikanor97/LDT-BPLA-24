import {User} from '@root/Types';


export declare namespace Api {
    type iRegistration = {
        name: string;
        email: string;
        password: string;
    }
    type oRegistration = User.Info;

    type iLogin = {
        username: string;
        password: string;
    }
    type oLogin = User.Token;
    type oMe = User.Info;
    type iRefreshToken = string;
    type oRefreshToken = User.Token;
    type oGetUsers = User.Info[];
}