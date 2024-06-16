import * as React from 'react';
import GridContainer from '@root/Components/GridContainer/GridContainer';
import ErrorImage from './Images/Error.png';
import styles from './404.module.scss';
import DefaultLayout from '@root/Layouts/Default/Default';
import {App} from '@root/Types';

type iError404 = {
    desc?: JSX.Element | string | null;
    hideCode?: boolean;
    title?: JSX.Element | string | null;
}

export const Error404:App.Page<iError404> = (props) => {
    return (
        <GridContainer className={styles.wrapper}>
            <div className={styles.content}>
                <div className={styles.img}>
                    <img 
                        src={ErrorImage}
                        alt="404"
                    />    
                </div>    
                {
                    !props.hideCode && (
                        <div className={styles.code}>
                            404
                        </div>
                    )
                }      
                {
                    props.title !== null && (
                        <div className={styles.title}>
                            {props.title || 'Страница не найдена :('}
                        </div>
                    )
                }
            </div>
        </GridContainer>
    )
}


Error404.getLayout = (page) => {
    return (
        <DefaultLayout>
            {page}
        </DefaultLayout>
    )
}


export default Error404