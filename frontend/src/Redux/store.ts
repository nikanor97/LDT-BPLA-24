import {combineReducers, configureStore} from '@reduxjs/toolkit';
import rootReducer from './rootReducer';
import createSagas, {Task} from 'redux-saga';
import rootSaga from "../Saga/rootSaga";
import {createReducerManager} from '@root/Utils/Redux/reducerManager/reducerManager';


const sagaMiddleware = createSagas();
const reducer = combineReducers(rootReducer);


const getStore = () => {
    const reducerManager = createReducerManager(rootReducer);
    const store = configureStore({
        reducer: reducerManager.reduce,
        middleware(getDefaultMiddleware) {
            return [
                ...getDefaultMiddleware({
                    thunk: false,
                    serializableCheck: false,
                    immutableCheck: true
                }),
                sagaMiddleware
            ];
        },
    });
    reducerManager.linkDispatch(store.dispatch);

    type Result = typeof store & {
        reducerManager: typeof reducerManager
        sagaMiddleware: typeof sagaMiddleware,
        sagaStore: {
            [key:string]: Task
        }
    };
    const result:Result = {
        ...store,
        reducerManager,
        sagaMiddleware,
        sagaStore: {}
    };
    sagaMiddleware.run(rootSaga);
    
    return result;
};


export type Reducers = typeof rootReducer;
export type AppState = ReturnType<typeof reducer>;
export type PageStateContainer<T> = AppState & {
    Pages?: Partial<T>
}
export type PageStateGeneric<T> = AppState & {
    Pages: T
}
export default getStore();