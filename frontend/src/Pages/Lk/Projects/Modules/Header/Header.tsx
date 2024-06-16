import * as React from 'react';
import {Row, Col, Button} from 'antd';
import styles from './Header.module.scss';
import {PlusOutlined} from '@ant-design/icons';
import { useDispatch} from 'react-redux';
import {PageActions} from '../../Redux/Store';
import { declinationOfNumber } from '@root/Utils/Normalize/declinationOfNumber';
import { useData } from '../../Hooks/useData';


const Header = () => {
    const dispatch = useDispatch();
    const data = useData();

    return (
        <div className={styles.wrapper}>
            <Row 
                align="middle"
                justify="space-between">
                <Col>
                    <div className={styles.title}>
                        Проекты
                    </div>    
                    {
                        data && (
                            <div className={styles.desc}>
                                Всего 
                                {' '}
                                {declinationOfNumber({
                                    value: data.length, 
                                    words: ['проект', 'проекта', 'проектов']
                                })}
                            </div>
                        )
                    }
                </Col>
                <Col>
                    <Button 
                        onClick={() => {
                            dispatch(PageActions.openCreateProject())
                        }}
                        icon={<PlusOutlined />}
                        type="primary">
                        Создать проект
                    </Button>
                </Col>
            </Row>
            
        </div>
    )
}


export default Header;