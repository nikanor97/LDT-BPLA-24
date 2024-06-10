import * as React from 'react';
import styles from './Sidebar.module.scss';
import Labels from './Modules/Labels/Labels';
import Scores from './Modules/Scores/Scores';
import {Tabs} from 'antd';
import { useVideo } from '../../Hooks/useVideo';

const Sidebar = () => {
    const video = useVideo();

    return (
        <div className={styles.wrapper}>
            <div className={styles.title}>
                Результаты модерации
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
            <Tabs 
                className={styles.tabs}
                defaultActiveKey='scores'

                items={[
                    {
                        key: 'labels',
                        label: 'Детекция',
                        children: <Labels />
                    },
                    {
                        key: 'scores',
                        label: 'Результаты мониторинга',
                        children: <Scores />
                    }
                ]}
            />
        </div>
    )
}


export default Sidebar;