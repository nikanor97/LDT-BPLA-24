import * as React from 'react';
import styles from './StatLineContainer.module.scss';
import { Tooltip } from 'antd';

type iStatLineContainer = {
    title: string;
    count1: number;
    count2: number;
    name1: string;
    name2: string;
}

const StatLineContainer = (props: iStatLineContainer) => {
    const { title, count1, count2, name1, name2 }  = props;
  
    const total = count1 + count2;
    let ratio1;
    let ratio2;
    if (total === 0) {
        ratio1 = 50;
        ratio2 = 50
    }
    if (count1 === 0 && count2 > 0) {
        ratio1 = 0;
        ratio2 = 100;
    }
    if (count2 === 0 && count1 > 0)  {
        ratio1  = 100;
        ratio2  = 0;
    } 
    if (count1 > 0 && count2 > 0){
        ratio1 = (count1 / total) * 100;
        ratio2 = (count2 / total) * 100;
    }
    
    return (
        <div className={styles.wrapper}>
            <div className={styles.title}>
                {title}
            </div>
            <div className={styles.content}>
                <div className={styles.lines}>
                    <Tooltip title={count1}>
                        <div style={{ width: `${ratio1}%`}} className={styles.lineLeft} />
                    </Tooltip>
                    <Tooltip title={count2}>
                        <div style={{ width: `${ratio2}%`}} className={styles.lineRight} />
                    </Tooltip>
                </div>
                <div className={styles.names}>
                    <div className={styles.nameBlock}>
                        <div className={styles.firstDot} />
                        <span className={styles.name}>{name1}</span>
                    </div>
                    <div className={styles.nameBlock}>
                        <div className={styles.secondDot} />
                        <span className={styles.name}>{name2}</span>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default StatLineContainer;