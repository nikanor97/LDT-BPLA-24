import * as React from 'react';
import Table from './Modules/Table/Table';
import Statistics from './Modules/Statistics/Statistics';
import styles from './TableTab.module.scss';


const TableTab = () => {
    return (
        <>
            <div className={styles.stats}>
                <Statistics />
            </div>
            <Table />
        </>
    )
}

export default TableTab;