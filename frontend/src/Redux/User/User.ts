import {createSlice, PayloadAction} from '@reduxjs/toolkit';
import {iActions, iState} from "./types";
import {getFullState, requestStart, requestSuccess, requestError} from '@root/Utils/Redux/RequestState/getRequestState';


const initialState:iState.Value = {
    Info: getFullState(),
    Token: getFullState()
};

const Slice = createSlice({
    initialState,
    name: 'User',
    reducers: {
        getToken: (state, action: PayloadAction<iActions.getToken>) => 
            requestStart(state.Token),
        _getTokenSuccess: (state, action: PayloadAction<iActions._getTokenSuccess>) => 
            requestSuccess(state.Token, action.payload),
        _getTokenError: (state) => 
            requestError(state.Token),
        
        getUserInfo: (state) =>
            requestStart(state.Info),
        _getUserInfoSuccess: (state, action: PayloadAction<iActions._getUserInfoSuccess>) => 
            requestSuccess(state.Info, action.payload),
        _getUserInfoError: (state) =>
            requestError(state.Info),

        logout: (state) => {
            state.Info = getFullState();
            state.Token = getFullState();
        }

    }
});

export const Actions = Slice.actions;
export default Slice.reducer;