import * as React from 'react';
import {Button} from 'antd';
import {LeftOutlined} from '@ant-design/icons';
import styles from './HeaderInfo.module.scss';
import {useHistory} from 'react-router-dom';
import routes from '@root/routes';
import {useSelector} from 'react-redux';
import {PageState} from '../../Redux/types';
import StatusTag from '@root/Components/StatusTag/StatusTag';
import { getStatusText, getStatusType } from '@root/Utils/Viewer/getStatus';
import ellipsisString from '@root/Utils/Normalize/ellipsisString';

const HeaderInfo = () => {
    const history = useHistory();
    const contentInfo = useSelector((state: PageState) => state.Pages.LkViewer.content.data?.info);

    return (
        <div className={styles.wrapper}>
            <Button 
                onClick={() => {
                    history.push(routes.lk.project(contentInfo?.project_id))           
                }}
                className={styles.btn}>
                <LeftOutlined />
            </Button>
            <div className={styles.title}>
                {contentInfo && ellipsisString({
                    type: "component",
                    text: contentInfo?.source_url,
                    length: 25,
                    tooltip: true
                })}
                {contentInfo && (<StatusTag 
                    type={getStatusType(contentInfo.status)}
                    text={getStatusText(contentInfo.status)}
                />)}
            </div>
        </div>
    )
}

export default HeaderInfo;