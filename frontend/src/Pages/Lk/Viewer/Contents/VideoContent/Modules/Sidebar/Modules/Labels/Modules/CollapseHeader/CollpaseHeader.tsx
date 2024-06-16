import * as React from 'react';
import {LabelIntervals} from '../../types';
import styles from './CollapseHeader.module.scss';
import {getDefaultColor} from '@root/Utils/Labels/getDefaultColor';
import {declinationOfNumber} from '@root/Utils/Normalize/declinationOfNumber';

type iCollapseHeader = {
    interval: LabelIntervals;
}

const CollapseHeader = (props: iCollapseHeader) => {
    const {interval} = props;
    const color = getDefaultColor(interval.label?.color);

    return (
        <div className={styles.group}>
            <div className={styles.mainInfo}>
                <div 
                    className={styles.color} 
                    style={{backgroundColor: color}}
                />
                <div className={styles.title}>
                    {interval.label?.description}
                </div>
            </div>
            <div className={styles.frames}>
                {declinationOfNumber({
                    words: ['Кадр', 'Кадра', 'Кадров'],
                    value: interval.framesCount
                })}
            </div>
        </div>
    )
}

export default CollapseHeader;