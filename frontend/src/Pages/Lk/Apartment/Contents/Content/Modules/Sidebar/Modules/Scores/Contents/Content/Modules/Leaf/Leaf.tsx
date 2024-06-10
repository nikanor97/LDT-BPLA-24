import * as React from 'react';
import {Apartment} from '@root/Types';
import styles from './Leaf.module.scss';


type iLeaf = {
    item: Apartment.Scores.LeafItem;
}

const Leaf = (props: iLeaf) => {
    const {item} = props;
    return (
        <div className={styles.wrapper}>
            <div className={styles.label}>
                {item.label}
            </div>
            <div className={styles.value}>
                {item.value}
            </div>
        </div>
    )
}

export default Leaf;