import React, {useEffect} from 'react';
import CS from '@root/Storages/Cookie';
import {useDispatch, useSelector} from 'react-redux';
import {AppState} from '@root/Redux/store';
import Actions from '@root/Redux/actions';
import Loader from '@root/Components/Loader/Loader';
import styles from './GetUser.module.scss';

type iGetUser = {
    children: JSX.Element;
}

const GetUser = (props: iGetUser) => {
    const state = useSelector((state:AppState) => state.User.Info);
    const token = useSelector((state:AppState) => state.User.Token.data);

    const dispatch = useDispatch();
    const refresh = CS.token.getRefresh();

    useEffect(() => {
        if (state.data) return;
        if (!refresh) {
            dispatch(Actions.User._getUserInfoSuccess(null));
        } else {
            dispatch(Actions.User.getUserInfo());
        }
    }, [state.data, token?.refresh_token]);

    if (!refresh) return props.children;
    else {
        if (state.fetching && !state.data) return (
            <div className={styles.loader}>
                <Loader />
            </div>
        )
    }
    return props.children;
}

export default GetUser;