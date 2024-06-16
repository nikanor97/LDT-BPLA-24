import * as React from 'react';
import Layout from '../../Modules/Layout/Layout';
import {Skeleton} from 'antd';
import styles from './Loading.module.scss';

const Loading = () => {
    return (
        <Layout 
            items={new Array(3).fill('').map((item, index) => (
                <Skeleton.Button 
                    key={index} 
                    className={styles.loader}
                />
            ))}
        />
    )
}

export default Loading;