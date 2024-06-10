import React, {useMemo} from 'react';
import GridContainer from '@root/Components/GridContainer/GridContainer';
import ErrorImage from './Images/error.png'
import DefaultLayout from '@root/Layouts/Default/Default';
import styles from './401.module.scss';
import {Link} from 'react-router-dom';
import routes from '@root/routes';

type iPage401 = {
    mode: 'unauth' | 'invalid_role';
    showTitle?: boolean;
}

const Page401 = (props: iPage401) => {
    const desc = useMemo(() => {
        switch (props.mode) {
            case 'unauth':
                return (
                    <>
                        Для просмотра данной страницы вам необходимо 
                        {' '}
                        <Link to={routes.login}>
                            авторизоваться
                        </Link>
                    </>
                )
            case 'invalid_role':
                return (
                    <>
                        Просмотр данной страницы для вашей роли недоступен
                    </>
                )
            default:
                return (
                    <>
                        Запрашиваемые данные не найдены или у вас отсутствует доступ к ним
                    </>
                )
        }
    }, [props.mode]);

    return (
        <DefaultLayout>
            <GridContainer className={styles.wrapper}>
                <div className={styles.content}>
                    <div className={styles.img}>
                        <img 
                            src={ErrorImage}
                            alt="401"
                        />    
                    </div>          
                    <div className={styles.code}>
                        401
                    </div>
                    <div className={styles.title}>
                        Отказано в доступе
                    </div>
                    <div className={styles.desc}>
                        {desc}
                    </div>
                </div>
            </GridContainer>
        </DefaultLayout>
    )
}


export default Page401;