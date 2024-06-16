import rootSagaCreator from "../rootSagaCreator";
import UserInfo from './UserInfo';
import Login from './Login'

export default function* rootSaga() {
    yield rootSagaCreator([
        UserInfo,
        Login
    ], 'USER');
}