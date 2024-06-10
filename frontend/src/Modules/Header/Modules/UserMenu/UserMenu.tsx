import * as React from 'react';
import {UserOutlined, LogoutOutlined} from '@ant-design/icons';
import {Avatar, Menu} from 'antd';
import {useDispatch, useSelector} from 'react-redux';
import {AppState} from '@root/Redux/store';
import styles from './UserMenu.module.scss';
import Actions from '@root/Redux/actions';
import CS from '@root/Storages/Cookie';
import { getUserAvatar } from '@root/Utils/User/getUserAvatar/getUserAvatar';

const UserMenu = () => {
    const user = useSelector((state:AppState) => state.User.Info.data);
    const dispatch = useDispatch();

    if (!user) return null;
    return (
        <div className={styles.wrapper}>
            <div className={styles.user}>
                <Avatar 
                    src={getUserAvatar(user.id)}
                    className={styles.avatar}
                    size={42}>
                    <UserOutlined />
                </Avatar>
                <div className={styles.userInfo}>
                    <div className={styles.name}>
                        {user.name}
                    </div>
                    <div className={styles.email}>
                        {user.email}
                    </div>
                </div>
            </div>
            <Menu 
                className={styles.menu}
                items={[
                    {
                        label: 'Выйти',
                        key: 'logout',
                        icon: <LogoutOutlined />,
                        className: styles.logout,
                        onClick: () => {
                            CS.token.clear();
                            dispatch(Actions.User.logout());
                        }
                    }
                ]}
            />
        </div>
    )
}

export default UserMenu;