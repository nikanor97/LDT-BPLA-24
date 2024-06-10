import * as React from 'react';
import {App} from '@root/Types';
import RegistrationForm from './Modules/RegistrationForm/RegistrationForm';
import AuthBox from '@root/Modules/AuthBox/AuthBox';
import styles from './Registration.module.scss';
import Background from './Img/Background.png';
import PageStateContainer from '@root/Containers/PageState/PageState';
import {Slice} from './Redux/Store';
import Sagas from './Saga/Registration';


const RegistrationPage:App.Page = () => {
    return (
        <PageStateContainer params={[Slice, [Sagas]]}>
            <div className={styles.wrapper}>
                <div className={styles.content}>
                    <AuthBox className={styles.box}>
                        <RegistrationForm />
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

RegistrationPage.getLayout = (page) => {
    return page
}

export default RegistrationPage;