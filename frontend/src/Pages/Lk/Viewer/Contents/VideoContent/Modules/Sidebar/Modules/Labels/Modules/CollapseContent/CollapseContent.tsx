import * as React from 'react';
import {LabelIntervals} from '../../types';
import {Tag} from 'antd';
import {getTimeInMinute} from '@root/Utils/Date/NormilizeTime';
import styles from './CollapseContent.module.scss';
import { useDispatch, useSelector } from 'react-redux';
import {PageActions} from '../../../../../../../../Redux/Store';
import classnames from 'classnames';
import {PageState} from '../../../../../../../../Redux/types';

type iCollapseContent = {
    interval: LabelIntervals;
}

const CollapseContent = (props: iCollapseContent) => {
    const dispatch = useDispatch();
    const activeKey = useSelector((state: PageState) => state.Pages.LkViewer.playInterval?.key);
    return (
        <div>
            {
                props.interval.result.map((interval) => {
                    const from = getTimeInMinute(interval.start);
                    const to =  getTimeInMinute(interval.end);
                    const key = `${props.interval.label?.name}:${from}-${to}`
                    const text = from === to
                        ? from
                        : `${from} - ${to}`;
                    const className = classnames(styles.tag, {
                        [styles.tagActive]: activeKey && activeKey === key
                    })

                    return (
                        <Tag 
                            key={key}
                            onClick={() => {
                                dispatch(PageActions.setPlayInterval({
                                    start: interval.start,
                                    end: interval.end,
                                    key
                                }))
                            }}
                            className={className}>
                            {text}
                        </Tag>
                    )
                })
            }
        </div>
    )
}

export default CollapseContent