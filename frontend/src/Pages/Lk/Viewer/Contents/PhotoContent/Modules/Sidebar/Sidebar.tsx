import * as React from 'react';
import styles from './Sidebar.module.scss';
import Labels from './Modules/Labels/Labels';
import { usePhoto } from '../../Hooks/usePhoto';

const Sidebar = () => {
    const photo = usePhoto();

    //TODO Поменять ручку скачивания результатов

    return (
        <div className={styles.wrapper}>
            <div className={styles.title}>
                Обнаруженные объекты
                {
                    photo && (
                        <a 
                            download="Result.txt"
                            href={`/api/v1/projects/download_detect_result?content_id=${photo.content_id}`}> 
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