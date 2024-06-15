import * as React from 'react';
import {Form, Button} from 'antd';
import {Input} from '@root/Components/Controls';
import styles from './LoginForm.module.scss';
import {Link} from 'react-router-dom'
import routes from '@root/routes';
import {Api} from '@root/Api/User/types';
import {useDispatch, useSelector} from 'react-redux';
import {PageState} from '../../Redux/types';
import {PageActions} from '../../Redux/Store';


const LoginForm = () => {
    const state = useSelector((state: PageState) => state.Pages.Login.login);
    const dispatch = useDispatch();
    return (
        <div>
            <div className={styles.title}>
                Авторизация
            </div>
            <div className={styles.form}>
                <Form<Api.iLogin> 
                    layout="vertical" 
                    onFinish={(values) => {
                        dispatch(PageActions.login(values))
                    }}>
                    <Form.Item 
                        name="username"
                        rules={[
                            {
                                required: true,
                                message: 'Поле обязательно для заполнения'
                            }
                        ]}
                        label="Логин">
                        <Input 
                            placeholder="Введите логин"
                        />
                    </Form.Item>
                    <Form.Item 
                        name="password"
                        rules={[
                            {
                                required: true,
                                message: 'Поле обязательно для заполнения'
                            }
                        ]}
                        label="Пароль">
                        <Input.Password 
                            placeholder="Введите пароль"
                        />
                    </Form.Item>
                    <Button 
                        className={styles.submit}
                        type="primary"
                        size="large"
                        loading={state.fetching}
                        htmlType="submit">
                        Войти
                    </Button>
                    <div className={styles.registration}>
                        <Link to={routes.registration}>
                            Зарегистрироваться
                        </Link>
                    </div>
                </Form>
            </div>
        </div>       
    )
}

export default LoginForm;