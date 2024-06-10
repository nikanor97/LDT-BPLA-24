import * as React from 'react';
import {Button} from 'antd';
import {InfoCircleOutlined, UploadOutlined} from '@ant-design/icons';
import styles from './HeaderContent.module.scss';
import { useDispatch } from 'react-redux';
import {PageActions} from '../../../../Redux/Store';
import {Space} from 'antd';


const HeaderContent = () => {
    const dispatch = useDispatch();
    return (
        <div className={styles.wrapper}>
            <Space>
                <Button 
                    icon={<UploadOutlined />}
                    
                    onClick={() => {
                        dispatch(PageActions.openUploadDrawer())
                    }}
                    type="primary">
                    Загрузить видео
                </Button>
                <Button 
                    icon={<InfoCircleOutlined />}
                    onClick={() => {
                        dispatch(PageActions.openApartmentDrawer())
                    }}
                    type="default">
                    Информация о квартире
                </Button>
            </Space>
        </div>
    )
}

export default HeaderContent;