import * as React from 'react';
import Loader from '@root/Components/Loader/Loader';
import styles from './Loading.module.scss';

const Loading = () => {
    return (
        <div className={styles.wrapper}>
            <Loader 
                text="Загрузка результатов мониторинга..."
            />
        </div>
    )
}

export default Loading;