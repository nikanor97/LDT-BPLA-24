import * as React from 'react';
import PageLoader from '@root/Components/Loader/Loader';
import styles from './Loading.module.scss'


const Loading = () => {
    return (
        <div className={styles.wrapper}>
            <PageLoader />
        </div>
    )
}


export default Loading;