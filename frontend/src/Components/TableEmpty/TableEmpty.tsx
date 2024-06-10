import * as React from 'react';
import Folders from './Img/Folders';
import styles from './TableEmpty.module.scss';


type iEmpty = {
    text: string | JSX.Element;
}

const Empty = (props: iEmpty) => {
    return (
        <div className={styles.wrapper}>
            <Folders />
            <div className={styles.title}>
                {props.text}
            </div>
        </div>
    )
}


export default Empty;