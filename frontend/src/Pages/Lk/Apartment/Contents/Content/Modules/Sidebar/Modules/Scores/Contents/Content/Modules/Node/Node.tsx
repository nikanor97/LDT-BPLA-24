import * as React from 'react';
import {Collapse} from 'antd';
import {Apartment} from '@root/Types';
import Controller from '../Controller/Controller';
import styles from './Node.module.scss';


type iNode = {
    item: Apartment.Scores.NodeItem;
    itemKey: string;
}

const Node = (props: iNode) => {
    const {item} = props;
    return (
        <Collapse 
            defaultActiveKey={props.itemKey}
            className={styles.collapse}>
            <Collapse.Panel 
                key={props.itemKey}
                header={item.label}>
                {
                    Object.entries(item.value)
                        .map(([key, item]) => {
                            if (['label', 'value'].includes(key)) return null;
                            return (
                                <Controller 
                                    item={item}
                                    itemKey={`${props.itemKey}/${key}`}
                                    key={`${props.itemKey}/${key}`}
                                />
                            )
                        })
                }
            </Collapse.Panel>
        </Collapse>
    )
}

export default Node;