import React from 'react';
import styles from './GridContainder.module.scss';
import classNames from 'classnames';
import {App} from "@types";

type iGridContainerProps = {
    children: App.children | App.children[];
    className?: string;
}

const GridContainer = (props:iGridContainerProps) => {
    const classes = {
        wrapper: classNames(
            styles.container,
            props.className,
        )
    };
    return (
        <div
            className={classes.wrapper}>
            {props.children}
        </div>
    );
};

export default GridContainer;