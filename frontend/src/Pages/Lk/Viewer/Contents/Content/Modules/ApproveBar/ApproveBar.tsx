import * as React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {PageState} from '../../../../Redux/types';
import GridContainer from '@root/Components/GridContainer/GridContainer';
import {Space, Button} from 'antd';
import styles from './Approvebar.module.scss';
import {PageActions} from '../../../../Redux/Store';

const ApproveBar = () => {
    const data = useSelector((state: PageState) => state.Pages.LkViewer.videos.data?.video);
    const state = useSelector((state:PageState) => state.Pages.LkViewer.videoStatus);
    const dispatch = useDispatch();
    if (!data) return null;
    if (data.status === 'approved') return null;
    if (data.status === 'declined') return null;

    return (
        <div className={styles.wrapper}>
            <GridContainer>
                <div>
                    <Space size={12}>
                        <Button 
                            type="primary"
                            loading={state.fetching}
                            onClick={() => {
                                dispatch(PageActions.changeVideoStatus({
                                    video_id: data.id,
                                    new_status: 'declined'
                                }))
                            }}
                            danger>
                            Отклонить
                        </Button>
                        <Button 
                            onClick={() => {
                                dispatch(PageActions.changeVideoStatus({
                                    video_id: data.id,
                                    new_status: 'approved'
                                }))
                            }}
                            loading={state.fetching}
                            type="primary">
                            Принять
                        </Button>
                    </Space>
                </div>
            </GridContainer>
        </div>
    )
}

export default ApproveBar;