import * as React from 'react';
import styles from './Labels.module.scss';
import {usePhoto} from '../../../../Hooks/usePhoto';
import {Collapse} from 'antd';
import {useLabelsIntervals} from './Hooks/useLabelsIntervals';
import CollapseHeader from './Modules/CollapseHeader/CollpaseHeader';

const Labels = () => {
    const labelsIntervals = useLabelsIntervals();
    const photo = usePhoto();
    if (!photo) return null;
    if (!labelsIntervals) return null;

    // if (video.status === 'created') {
    //     return (
    //         <div className={styles.empty}>
    //             Детекция выполняется. Результаты будут доступны позже...
    //         </div>
    //     )
    // }

    return (
        <div className={styles.wrapper}>
            <Collapse className={styles.collapse}>
                {
                    labelsIntervals
                        .map((interval, index) => {
                            if (!interval.label) return null;
                            return (
                                <CollapseHeader interval={interval} />
                            )
                        })
                }
            </Collapse>
        </div>
    )
}


export default Labels;