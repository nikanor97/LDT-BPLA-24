import * as React from 'react';
import styles from './Sidebar.module.scss';
import Labels from './Modules/Labels/Labels';
import { useVideo } from '../../Hooks/useVideo';

const Sidebar = () => {
    const video = useVideo();

    //TODO Поменять ручку скачивания результатов

    return (
        <div className={styles.wrapper}>
            <div className={styles.title}>
                Обнаруженные объекты
                {
                    video && (
                        <a 
                            download="Score_map.csv"
                            href={`/api/v1/projects/download-score-map?video_id=${video.id}`}> 
                            Скачать результаты
                        </a>
                    )
                }
            </div>
            <Labels />
        </div>
    )
}


export default Sidebar;