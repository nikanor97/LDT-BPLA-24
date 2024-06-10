import {RequestFullState, RequestShortState, State, isFullState} from './types';

export function requestSuccess(state:RequestShortState):void;
export function requestSuccess<T>(state:RequestFullState<T>, data: T):void;
export function requestSuccess<T>(state:State<T>, data?: T) {
    state.error = false;
    state.loaded = true;
    state.fetching = false;
    if (isFullState(state) && data) {
        state.data = data;
    }
}

export const getShortState = ():RequestShortState => {
    return {
        errMsg: '',
        error: false,
        fetching: false,
        loaded: false
    };
};

export const getFullState = <T>():RequestFullState<T> => {
    const short = getShortState();
    return {
        ...short,
        data: null
    };
};

export const requestStart = (state: State<unknown>) => {
    state.error = false;
    state.fetching = true;
};
export const requestError = (state: State<unknown>, message?: string) => {
    state.error = true;
    state.fetching = false;
    if (message) state.errMsg = message;
};