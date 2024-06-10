import * as React from 'react';
import { useSelector } from 'react-redux';
import {PageState} from '../../../../../../../../Redux/types';
import {Collapse} from 'antd';
import Controller from './Modules/Controller/Controller'
import styles from './Content.module.scss';

const Content = () => {
    const data = useSelector((state: PageState) => state.Pages.LkApartment.sidebarScores.data);
    if (!data) return null;

    return (
        <div className={styles.wrapper}>
            {
                Object.entries(data)
                    .map(([key, value]) => (
                        <Controller 
                            key={key}
                            item={value}
                            itemKey={key}
                        />
                    ))
            }
        </div>
    )
}

export default Content;