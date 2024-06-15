import * as React from 'react';
import styles from './StatDonutContainer.module.scss';
import { DonutDiagramPercents } from '../DonutDiagramPercents/DonutDiagramPercents';
import Hint from '../Hint/Hint';

type iStatDonutContainer = {
    title: string;
    count: number;
    total: number;
    color: string;
    hint?: string;
}

const StatDonutContainer = (props: iStatDonutContainer) => {
    return (
        <div className={styles.wrapper}>

            <div className={styles.content}>
                <div className={styles.donut}>
                    <DonutDiagramPercents 
                        usedCount={props.count}
                        totalCount={props.total}
                        color={props.color}
                    />
                </div>
                <div className={styles.text}>
                    <div className={styles.value}>
                        <span>
                            {props.count}
                        </span>
                        {
                            props.total !== undefined && (
                                <>
                                    <span className={styles.total}>
                                        /{props.total}
                                    </span>
                                </>
                            )
                        }
                    </div>
                    <div className={styles.title}>
                        {props.title} {props.hint !== undefined && (<Hint title={props.hint}/>)}
                    </div>
                </div>

            </div>
        </div>
    )
}

export default StatDonutContainer;