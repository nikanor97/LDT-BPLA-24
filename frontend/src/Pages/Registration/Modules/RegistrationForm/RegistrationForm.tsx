import * as React from 'react';
import {Form, Button} from 'antd';
import {Input} from '@root/Components/Controls';
import styles from './RegistrationForm.module.scss';
import {Link} from 'react-router-dom'
import routes from '@root/routes';
import {useDispatch, useSelector} from 'react-redux';
import {PageActions} from '../../Redux/Store';
import {PageState} from '../../Redux/types';
import {FormData} from '../../types';
import {omit} from 'lodash';

const RegistrationForm = () => {
    const dispatch = useDispatch();
    const state = useSelector((state:PageState) => state.Pages.Registration.registration);
    return (
        <div>
            <div className={styles.title}>
                Регистрация
            </div>
            <div className={styles.form}>
                <Form<FormData> 
                    layout="vertical" 
                    onFinish={(values) => {
                        dispatch(PageActions.registration(omit(values, 'passwordConfirm')))
                    }}>
                    <Form.Item 
                        name="name"
                        rules={[{
                            required: true,
                            message: 'Поле обязательно для заполнения'
                        }]}
                        label="Имя">
                        <Input 
                            placeholder="Введите ваше имя"
                        />
                    </Form.Item>
                    <Form.Item 
                        name="email"
                        rules={[{
                            required: true,
                            message: 'Поле обязательно для заполнения'
                        }]}
                        label="Email">
                        <Input 
                            placeholder="Введите ваш e-mail"
                        />
                    </Form.Item>
                    <Form.Item 
                        name="password"
                        rules={[{
                            required: true,
                            message: 'Поле обязательно для заполнения'
                        }]}
                        label="Пароль">
                        <Input.Password 
                            placeholder="Введите пароль"
                        />
                    </Form.Item>
                    <Form.Item 
                        name="passwordConfirm"
                        rules={[
                            {
                                required: true,
                                message: 'Поле обязательно для заполнения'
                            },
                            ({getFieldValue}) => ({
                                validator(_, value) {
                                    if (!value || getFieldValue('password') === value) {
                                        return Promise.resolve();
                                    }
                                    return Promise.reject(new Error('Пароли не совпадают'));
                                },
                            }),

                        ]}
                        dependencies={['password']}
                        label="Подтверждение пароля">
                        <Input.Password 
                            placeholder="Введите пароль еще раз"
                        />
                    </Form.Item>
                    <Button 
                        className={styles.submit}
                        loading={state.fetching}
                        type="primary"
                        size="large"
                        htmlType="submit">
                        Зарегистрироваться
                    </Button>
                    <div className={styles.registration}>
                        <Link to={routes.login}>
                            Уже есть аккаунт?
                        </Link>
                    </div>
                </Form>
            </div>
        </div>       
    )
}

export default RegistrationForm;