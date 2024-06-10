import * as React from 'react';
import styles from './ChartContainer.module.scss';


type iChartContainer = {
    title: JSX.Element;
    children: JSX.Element;
    desc?: JSX.Element;
}

const ChartContainer = (props: iChartContainer) => {
    return (
        <div className={styles.wrapper}>
            <div className={styles.title}>
                {props.title}
                {
                    props.desc && (
                        <div className={styles.desc}>
                            {props.desc}
                        </div>
                    )
                }
            </div>
            {props.children}
        </div>
    )
}


export default ChartContainer;