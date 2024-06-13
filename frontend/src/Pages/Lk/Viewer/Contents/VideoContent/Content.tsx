import * as React from 'react';
import GridContainer from '@root/Components/GridContainer/GridContainer';
import Sidebar from './Modules/Sidebar/Sidebar';
import Workspace from './Modules/Workspace/Workspace';
import ApproveBar from './Modules/ApproveBar/ApproveBar';
import styles from './Content.module.scss';

const Content = () => {
    console.log('Content');
    return (
        <div className={styles.wrapper}>
            <div className={styles.row}>
                <div className={styles.workspace}>
                    <GridContainer className={styles.workspaceContainer}>
                        <Workspace />
                    </GridContainer>
                </div>
                <Sidebar />
            </div>
            <ApproveBar />
        </div>
    )
}

export default Content;