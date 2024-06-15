import * as React from 'react';
import styles from './StatContainer.module.scss';

type iStatContainer = {
    title: string;
    icon: JSX.Element;
    count: number | JSX.Element;
    total?: number | JSX.Element;
}

const StatContainer = (props: iStatContainer) => {
    return (
        <div className={styles.wrapper}>
            <div className={styles.title}>
                {props.title}
            </div>
            <div className={styles.content}>
                <div className={styles.icon}>
                    {props.icon}
                </div>
                <div className={styles.value}>
                    <span>
                        {props.count}
                    </span>
                    {
                        props.total !== undefined && (
                            <>
                                {props.total}
                            </>
                        )
                    }
                </div>
            </div>
        </div>
    )
}

export default StatContainer;