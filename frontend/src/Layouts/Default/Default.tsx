import * as React from 'react';
import Header from '@root/Modules/Header/Header';
import styles from './Default.module.scss'

type iDefault = {
    children?: JSX.Element;
}

const Default = (props: iDefault) => {
    return (
        <>
            <div className={styles.wrapper}>
                <Header />
                <div className={styles.content}>
                    {props.children}
                </div>
            </div>
        </>
    )
}

export default Default;