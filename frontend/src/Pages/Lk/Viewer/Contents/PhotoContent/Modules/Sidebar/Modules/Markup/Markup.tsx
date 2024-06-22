import React from 'react';
import {useSelector} from "react-redux"
import {PageState} from '../../../../../../Redux/types';
import Label from './Modules/Label/Label';
import styles from './Markup.module.scss';

const Markup = () => {
    const labels = useSelector((state:PageState) => state.Pages.LkViewer.labels.data);
    if (!labels) return null;
    const labelsArray = Object.values(labels);
    return (
        <div className={styles.wrapper}>
            <div className={styles.labels}>
                {
                    labelsArray.map((label, index) => {
                        return (
                            <Label key={index} label={label} />
                        )
                    })
                }
            </div>

        </div>
    )
};

export default Markup;