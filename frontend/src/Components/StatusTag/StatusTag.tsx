import * as React from 'react';
import {Tag} from 'antd';
import styles from './StatusTag.module.scss';
import classnames from 'classnames';


export type StatusType = 'success' | 'default';
type iStatusTag = {
    text: string;
    type: StatusType;
    className?: string;
}

const StatusTag = (props: iStatusTag) => {
    const className = classnames(styles.tagWrapper, props.className, {
        [styles.success]: props.type === 'success',
        [styles.default]: props.type === 'default',
    })
    return (
        <div className={styles.tagWrapper}>
            <Tag className={className}>
                {props.text}
            </Tag>
        </div>
    )
}

StatusTag.defaultProps = {
    type: 'default'
}

export default StatusTag;