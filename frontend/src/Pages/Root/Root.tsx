import React, {useEffect} from 'react';
import Loader from '@root/Components/Loader/Loader';
import styles from './Root.module.scss';
import {useHistory} from 'react-router-dom';
import {useUserRoles} from '@root/Hooks/User/useUserRoles';
import routes from '@root/routes';

const RootPage = () => {
    const history = useHistory();
    const userRole = useUserRoles()

    useEffect(() => {
        if (!userRole.requested) return;
        if (userRole.auth) {
            history.push(routes.lk.projects)
        } else {
            history.push(routes.login)
        }
    }, [userRole.requested])

    return (
        <div className={styles.wrapper}>
            <Loader />
        </div>
    )
}

export default RootPage