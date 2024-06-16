import {getFullState, requestStart, requestSuccess, requestError} from '@root/Utils/Redux/RequestState/getRequestState';
import {createSlice, PayloadAction} from '@reduxjs/toolkit';
import {iState, iActions} from './types';

const initialState: iState.Value = {
    login: getFullState()
};


export const Slice = createSlice({
    name: 'Login',
    initialState,
    reducers: {
        login: (state, action: PayloadAction<iActions.login>) => 
            requestStart(state.login),
        _loginSuccess: (state, action: PayloadAction<iActions._loginSuccess>) => 
            requestSuccess(state.login, action.payload),
        _loginError: (state, action: PayloadAction<iActions._loginError>) => 
            requestError(state.login, action.payload),

    }   
});
export const PageActions = Slice.actions;
