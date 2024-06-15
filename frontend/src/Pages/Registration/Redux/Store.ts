import {getFullState, requestStart, requestSuccess, requestError} from '@root/Utils/Redux/RequestState/getRequestState';
import {createSlice, PayloadAction} from '@reduxjs/toolkit';
import {iState, iActions} from './types';

const initialState: iState.Value = {
    registration: getFullState()
};

export const Slice = createSlice({
    name: 'Registration',
    initialState,
    reducers: {
        registration: (state, action: PayloadAction<iActions.registration>) => 
            requestStart(state.registration),
        _registrationSuccess: (state, action: PayloadAction<iActions._registrationSuccess>) => 
            requestSuccess(state.registration, action.payload),
        _registrationError: (state, action: PayloadAction<iActions._registrationError>) => 
            requestError(state.registration, action.payload),

    }   
});

export const PageActions = Slice.actions;
