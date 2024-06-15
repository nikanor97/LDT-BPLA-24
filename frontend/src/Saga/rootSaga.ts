import rootSagaCreator from "./rootSagaCreator";
import User from './User';

export default function* rootSaga() {
    const sagas = [
        User
    ];
    yield rootSagaCreator(sagas, 'ROOT');
}