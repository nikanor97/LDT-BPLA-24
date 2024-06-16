import * as React from 'react';
import {Avatar} from 'antd';
import {UserOutlined} from '@ant-design/icons';
import styles from './UserTag.module.scss';

type iUserTag = {
    name: string;
    email?: string;
    avatar?: string;
}

const UserTag = (props: iUserTag) => {
    return (
        <div className={styles.wrapper}>
            <Avatar 
                src={props.avatar}
                size={30}>
                <UserOutlined />
            </Avatar>
            <div className={styles.content}>
                <div className={styles.name}>
                    {props.name}
                </div>
                {
                    props.email && (
                        <div className={styles.email}>
                            {props.email}
                        </div>
                    )
                }
            </div>
        </div>
    )
}

export default UserTag;