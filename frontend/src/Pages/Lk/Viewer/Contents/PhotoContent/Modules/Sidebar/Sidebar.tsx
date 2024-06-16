import * as React from 'react';
import styles from './Sidebar.module.scss';
import Labels from './Modules/Labels/Labels';
import { usePhoto } from '../../Hooks/usePhoto';
import { useDispatch } from 'react-redux';
import {PageActions} from '../../../../Redux/Store';
import { Button } from 'antd';

const Sidebar = () => {
    const photo = usePhoto();
    const dispatch = useDispatch();

    return (
        <div className={styles.wrapper}>
            <div className={styles.title}>
                Обнаруженные объекты
                {
                    photo && (
                        <Button
                            onClick={() => {
                                dispatch(PageActions.downloadResult({
                                    content_id: photo.content_id
                                }));
                            }}>
                            Скачать результаты
                        </Button>
                    )
                }
            </div>
            <Labels />
        </div>
    )
}


export default Sidebar;