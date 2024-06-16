import {combineReducers, AnyAction} from 'redux';
import {Reducers} from '@root/Redux/store';
import {PayloadAction, createSlice} from '@reduxjs/toolkit';
import {iActions, iState} from './types';
import moment from 'moment';
import {Dispatch} from 'react';

const initialState: iState.Value = {
    action: null,
    date: null,
    name: null
};

const initial = createSlice({
    name: 'initial',
    initialState,
    reducers: {
        changePage: (state, reduxAction:PayloadAction<iActions.changePage>) => {
            const {action, name} = reduxAction.payload;
            state.date = moment().toISOString();
            state.action = action;
            state.name = name;
        }
    }
});

export const Actions = initial.actions;

export const createReducerManager = (initialReducers:Reducers) => {

    const reducers:any = {
        ...initialReducers,
        Pages: {
            initial: initial.reducer
        }
    };
    let combinedReducer = combineReducers({
        ...reducers,
        Pages: combineReducers(reducers.Pages)
    });
    let keysToRemove:string[] = [];
    let dispatch: Dispatch<AnyAction> | null = null;
  
    return {
        getReducerMap: () => reducers,
        reduce: (state:any, action:PayloadAction<any>) => {
            const stateCopy = {...state};
            const statePages = {...stateCopy.Pages};

            if (keysToRemove.length) {
                for (const key of keysToRemove) {
                    delete statePages[key];
                }
                keysToRemove = [];
            }
            stateCopy.Pages = statePages;
            return combinedReducer(stateCopy, action as never);
        },
        linkDispatch: (storeDispatch: Dispatch<any>) => {
            if (dispatch) return;
            dispatch = storeDispatch;
        },
        add: (key: string, reducer: any) => {
            const pagesReducers = reducers.Pages;
            pagesReducers[key] = reducer;
            combinedReducer = combineReducers({
                ...reducers,
                Pages: combineReducers(pagesReducers)
            });
            if (dispatch) {
                dispatch(Actions.changePage({
                    action: 'add',
                    name: key
                }));
            }
        },
        remove: (key: string) => {
            const pagesReducers = reducers.Pages;
            delete pagesReducers[key];
            combinedReducer = combineReducers({
                ...reducers,
                Pages: combineReducers(pagesReducers)
            });
            keysToRemove.push(key);
            if (dispatch) {
                dispatch(Actions.changePage({
                    action: 'remove',
                    name: key
                }));
            }
        }
    };
};