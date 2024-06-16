import * as React from 'react';
import styles from './Sidebar.module.scss';
import Labels from './Modules/Labels/Labels';
import { useVideo } from '../../Hooks/useVideo';
import { Button } from 'antd';
import {PageActions} from '../../../../Redux/Store';
import { useDispatch } from 'react-redux';

const Sidebar = () => {
    const video = useVideo();
    const dispatch = useDispatch();

    return (
        <div className={styles.wrapper}>
            <div className={styles.title}>
                Обнаруженные объекты
                {
                    video && (
                        <Button
                            onClick={() => {
                                dispatch(PageActions.downloadResult({
                                    content_id: video.content_id
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