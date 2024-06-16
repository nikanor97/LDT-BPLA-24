import * as React from 'react';
import styles from './AuthBox.module.scss';
import {App} from '@root/Types';
import Logo from '@root/Img/Logo.png';
import classnames from 'classnames';

type iAuthBox = {
    children: App.children | App.children[];
    className?: string;
}

const AuthBox = (props: iAuthBox) => {
    return (
        <div className={classnames(styles.wrapper, props.className)}>
            <div className={styles.logo}>
                <img className={styles.logoImage} src={Logo} alt="logo"/>
            </div>
            {props.children}
        </div>
    )
}


export default AuthBox;