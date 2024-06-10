export type State<T> = RequestFullState<T> | RequestShortState;

export type RequestShortState = {
    fetching: boolean;
    error: boolean;
    loaded: boolean;
    errMsg: string;
}

export type RequestFullState<T> = RequestShortState & {
    data:T | null
}

export const isFullState = <T>(state:State<T>):state is RequestFullState<T> => {
    return 'data' in state;
};