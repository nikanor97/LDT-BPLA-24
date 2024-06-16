import * as React from 'react';
import styles from './Labels.module.scss';
import {usePhoto} from '../../../../Hooks/usePhoto';
import {Collapse} from 'antd';
import {useLabelsIntervals} from './Hooks/useLabelsIntervals';
import CollapseHeader from './Modules/CollapseHeader/CollpaseHeader';
import EmptyObject from '@root/Img/EmptyObjects.png'

const Labels = () => {
    const labelsIntervals = useLabelsIntervals();
    const photo = usePhoto();
    if (!photo) return null;
    if (!labelsIntervals) return null;

    if (photo.status === 'created') {
        return (
            <div className={styles.created}>
                Детекция выполняется. Результаты будут доступны позже...
            </div>
        )
    }

    if (labelsIntervals.length === 0) {
        return (
            <div className={styles.empty}>
                <img className={styles.image} src={EmptyObject} alt='empty'/>
                <span className={styles.text}>
                    Объектов не обнаружено
                </span>
            </div>
        )
    }


    console.log(labelsIntervals)

    return (
        <div className={styles.wrapper}>
            <Collapse className={styles.collapse}>
                {
                    labelsIntervals
                        .map((interval, index) => {
                            if (!interval.label) return null;
                            return (
                                <CollapseHeader interval={interval} key={index}/>
                            )
                        })
                }
            </Collapse>
        </div>
    )
}


export default Labels;