import * as React from 'react';
import {Button} from 'antd';
import {LeftOutlined} from '@ant-design/icons';
import styles from './HeaderInfo.module.scss';
import {useHistory} from 'react-router-dom';
import routes from '@root/routes';
import {useSelector} from 'react-redux';
import {PageState} from '../../../../Redux/types';
import StatusTag from '@root/Components/StatusTag/StatusTag';
import {getStatusText, getStatusType} from '@root/Utils/Viewer/getStatus';

const HeaderInfo = () => {
    const history = useHistory();
    const apartment = useSelector((state: PageState) => state.Pages.LkViewer.apartment.data);

    return (
        <div className={styles.wrapper}>
            <Button 
                onClick={() => {
                    history.push(routes.lk.project(apartment?.project_id))           
                }}
                className={styles.btn}>
                <LeftOutlined />
            </Button>
            <div className={styles.title}>
                Модерация видео
            </div>
            {
                apartment !== null && (
                    <StatusTag 
                        className={styles.tag}
                        text={getStatusText(apartment.status)}
                        type={getStatusType(apartment.status)}
                    />
                )
            }
        </div>
    )
}

export default HeaderInfo;