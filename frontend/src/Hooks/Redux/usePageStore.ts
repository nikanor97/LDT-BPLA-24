import store from '@root/Redux/store';
import {useEffect} from 'react';
import {Slice} from '@reduxjs/toolkit';
import {Saga} from 'redux-saga';
import rootSagaCreator from '@root/Saga/rootSagaCreator';

const {reducerManager, sagaMiddleware, sagaStore} = store;
type SagaGenerator = Saga<any[]>
type Settings = {
    removeStoreOnClose: boolean;
    removeSagaOnClose: boolean;
}
const defaultSettings:Settings = {
    removeSagaOnClose: false,
    removeStoreOnClose: true
};

const sagaCreator = function* (sagas: SagaGenerator[], name: string) {
    yield rootSagaCreator(sagas, `Pages/${name}`);
};


export const usePageStore = (slice: Slice<any, any, string>, sagas?: SagaGenerator[], settings?: Partial<Settings>) => {
    useEffect(() => {
        const sagaKey = `Pages/${slice.name}`;
        const mergeSettings = {
            ...defaultSettings,
            ...settings
        };

        if (sagas) {
            if (!sagaStore[sagaKey]) {
                const task = sagaMiddleware.run(sagaCreator, sagas, slice.name);
                sagaStore[sagaKey] = task;
            }
        }
        reducerManager.add(slice.name, slice.reducer);
        return () => {
            if (mergeSettings.removeStoreOnClose) {
                //Удаляем стор
                reducerManager.remove(slice.name);
            }
            if (mergeSettings.removeSagaOnClose) {
                if (sagaStore[sagaKey]) {
                    //Удаляем сагу
                    sagaStore[sagaKey].cancel();
                    delete sagaStore[sagaKey];
                }
            }
        };
    }, []);
};


export default usePageStore;