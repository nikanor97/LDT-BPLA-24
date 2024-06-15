import {useSelector} from "react-redux"
import {AppState} from '@root/Redux/store';
import {User} from '@root/Types';



export const useUserRoles = () => {
    const info = useSelector((state: AppState) => state.User.Info);

    const result: User.SystemRolesValues = {
        requested: info.loaded,
        auth: info.data !== null,
        unauth: info.data === null
    }
    return result;
}