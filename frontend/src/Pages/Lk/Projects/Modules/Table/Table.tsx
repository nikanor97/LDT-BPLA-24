import React from 'react';
import ContentController from './Controllers/ContentController'
import styles from './Table.module.scss';


const TableModule = () => {
    
    return (
        <div className={styles.wrapper}>
            <ContentController />
        </div>
    )
}


export default TableModule;