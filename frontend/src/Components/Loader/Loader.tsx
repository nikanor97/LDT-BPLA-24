import * as React from 'react';
import styles from './Loader.module.scss';
import classnames from 'classnames';

type iLoader = {
    text: string | JSX.Element;
}

const Loader = (props: iLoader) => {
    return (
        <div className={styles.wrapper}>
            <div className={styles.loaderWrapper}>
                <div className={styles.loader}>
                    {
                        new Array(6)
                            .fill('')
                            .map((item, index) => (
                                <div 
                                    className={classnames(styles.item, styles[`item-${index + 1}`])}
                                    key={index}>
                                    <div className={styles.itemLighter} />
                                    <div className={styles.itemDarker} />
                                </div>
                            ))
                    }
                </div>
            </div>
            <div className={styles.text}>
                {props.text}
            </div>
        </div>
    )
}

export default Loader;