import * as React from 'react';
import styles from './Labels.module.scss';
import {useVideo} from '../../../../Hooks/useVideo';
import {Collapse} from 'antd';
import {useLabelsIntervals} from './Hooks/useLabelsIntervals';
import CollapseHeader from './Modules/CollapseHeader/CollpaseHeader';
import CollapseContent from './Modules/CollapseContent/CollapseContent';

const Labels = () => {
    const labelsIntervals = useLabelsIntervals();
    const video = useVideo();
    if (!video) return null;
    if (!labelsIntervals) return null;

    if (video.status === 'created') {
        return (
            <div className={styles.empty}>
                Детекция выполняется. Результаты будут доступны позже...
            </div>
        )
    }

    return (
        <div className={styles.wrapper}>
            <Collapse className={styles.collapse}>
                {
                    labelsIntervals
                        .map((interval, index) => {
                            if (!interval.label) return null;
                            return (
                                <Collapse.Panel 
                                    key={`${interval.label.name}${index}`}
                                    header={<CollapseHeader interval={interval} />}>
                                    <CollapseContent 
                                        interval={interval} 
                                    />
                                </Collapse.Panel>
                            )
                        })
                }
            </Collapse>
        </div>
    )
}


export default Labels;