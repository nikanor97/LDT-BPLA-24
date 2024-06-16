import * as React from 'react';
import {useSelector} from 'react-redux';
import {AppState} from '@root/Redux/store';
import {Button, Avatar, Dropdown} from 'antd';
import {Link} from 'react-router-dom'
import routes from '@root/routes';
import {UserOutlined} from '@ant-design/icons';
import UserMenu from '../UserMenu/UserMenu';
import styles from './UserAvatar.module.scss';
import { getUserAvatar } from '@root/Utils/User/getUserAvatar/getUserAvatar';


const UserAvatar = () => {
    const userInfo = useSelector((state: AppState) => state.User.Info.data);

    if (!userInfo) {
        return (
            <Link to={routes.login}>
                <Button type="primary">
                    Войти
                </Button>
            </Link>
        )
    } else {
        const avatar = getUserAvatar(userInfo.id);
        return (
            <>
                <Dropdown 
                    dropdownRender={(props) => {
                        return (
                            <div className={styles.dropdown}>
                                <UserMenu />
                            </div>
                        )
                    }}>
                    <Avatar 
                        src={avatar}
                        style={{fontSize: '16px'}}  
                        size={32}>
                        <UserOutlined />
                    </Avatar>
                </Dropdown>
            </>
        )
    }
}

export default UserAvatar;