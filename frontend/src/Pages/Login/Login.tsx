import * as React from 'react';
import {App} from '@root/Types';
import LoginForm from './Modules/LoginForm/LoginForm';
import AuthBox from '@root/Modules/AuthBox/AuthBox';
import styles from './Login.module.scss';
import Background from '@root/Img/Copter.png';
import PageStateContainer from '@root/Containers/PageState/PageState';
import {Slice} from './Redux/Store';
import LoginSaga from './Saga/LoginSaga';

const LoginPage:App.Page = () => {
    return (
        <PageStateContainer params={[Slice, [LoginSaga]]}>
            <div className={styles.wrapper}>
                <div className={styles.content}>
                    <AuthBox className={styles.box}>
                        <LoginForm />
                    </AuthBox>

                </div>
                <img 
                    className={styles.background}
                    src={Background} 
                    alt="background" 
                />
            </div>
        </PageStateContainer>
    )
}

LoginPage.getLayout = (page) => {
    return page
}

export default LoginPage;