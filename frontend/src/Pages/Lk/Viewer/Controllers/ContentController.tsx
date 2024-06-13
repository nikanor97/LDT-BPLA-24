import * as React from 'react';
import {useSelector } from 'react-redux';
import {PageState} from '../Redux/types';
import {Result} from 'antd';
import VideoContent from '../Contents/VideoContent/Content';
import Loader from '@root/Components/Loader/Loader';
import styles from './ContentController.module.scss';

const ContentController = () => {
    const state = useSelector((state:PageState) => state.Pages.LkViewer.content)
    const labels = useSelector((state:PageState) => state.Pages.LkViewer.labels)

    console.log(labels)

    if (state.fetching || labels.fetching) return (
        <div className={styles.loader}>
            <Loader text="Загрузка видео данных..." />
        </div>
    )

    if (state.loaded && labels.loaded) {
        if (state.data && labels.data) {
            if (state.data.info) {
                if (state.data.info.content_type === "video") {
                    return <VideoContent />
                } else return null; //TODO Сюда контент по фото
                
            } else return (
                <div className={styles.error}>
                    <Result
                        status="404"
                        title="Видео отсутствуют"
                    />
                </div>
            )
        }
    }
    
    if (state.error || labels.error) return (
        <div className={styles.error}>
            <Result 
                status={500}
                title="Ошибка при получении данных"
            />
        </div>
    )


    return null;
}

export default ContentController;