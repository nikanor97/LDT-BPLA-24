import { Project } from '@root/Types'
import React, { useEffect } from 'react'
import classnames from 'classnames'
import { useDispatch, useSelector } from 'react-redux'
import {PageActions} from '../../../../../../../../Redux/Store';
import { PageState } from '../../../../../../../../Redux/types';
import styles from './Label.module.scss'
import { Radio } from 'antd';

type LabelProps = {
    label: Project.Label.Item;
}

const Label = (props: LabelProps) => {
    const selectedLabel  = useSelector((state: PageState)=> state.Pages.LkViewer.selectedLabel);
    const dispatch = useDispatch();

    const className = classnames(styles.wrapper, {
        [styles.selected]: selectedLabel?.id === props.label.id
    })

    useEffect(()  =>  {
        return () => {
            dispatch(PageActions.eraseSelectedLabel())
        }
    }, []);

    return (
        <div
            className={className}
            onClick={() => {
                dispatch(PageActions.setSelectedLabel(props.label))
            }}>
            <div className={styles.info}>
                <div 
                    className={styles.color} 
                    style={{backgroundColor: props.label.color}}
                />
                <div className={styles.title}>
                    {props.label.description}
                </div>
            </div>
            <Radio checked={selectedLabel?.id === props.label.id}/>
        </div>
    )
}

export default Label;