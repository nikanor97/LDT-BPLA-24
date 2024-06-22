import * as React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {PageState} from '../../../../Redux/types';
import GridContainer from '@root/Components/GridContainer/GridContainer';
import {Space, Button} from 'antd';
import styles from './Approvebar.module.scss';
import {PageActions} from '../../../../Redux/Store';
import useGetPrevAndNextIds from '@root/Pages/Lk/Viewer/Hooks/useGetPrevAndNextIds';
import { useHistory } from 'react-router-dom';
import routes from '@root/routes';
import Previous from '@root/Icons/Previous';
import Next from '@root/Icons/Next';

const ApproveBar = () => {
    const data = useSelector((state: PageState) => state.Pages.LkViewer.content.data?.info);
    const state = useSelector((state:PageState) => state.Pages.LkViewer.videoStatus);
    const viewMode = useSelector((state:PageState)  => state.Pages.LkViewer.viewMode);
    const {previousId, nextId} = useGetPrevAndNextIds();
    const history  = useHistory();
    const dispatch = useDispatch();
    if (!data) return null;

    return (
        <div className={styles.wrapper}>
            <GridContainer>
                <div>
                    <Space size={12}>
                        <Button
                            onClick={() => {
                                dispatch(PageActions.setViewMode(viewMode === "markup" ? "result" : "markup"))
                            }}
                        >
                            {viewMode === "markup" ?  "Закончить разметку"  :  "Разметить"}
                        </Button>
                        {(data.status !== 'approved' && data.status !== 'declined' && viewMode === "result") && (
                            <>
                                <Button 
                                    type="primary"
                                    loading={state.fetching}
                                    onClick={() => {
                                        dispatch(PageActions.changeContentStatus({
                                            content_id: data.content_id,
                                            new_status: 'declined'
                                        }))
                                    }}
                                    danger>
                            Отклонить
                                </Button>
                                <Button 
                                    onClick={() => {
                                        dispatch(PageActions.changeContentStatus({
                                            content_id: data.content_id,
                                            new_status: 'approved'
                                        }))
                                    }}
                                    loading={state.fetching}
                                    type="primary">
                            Принять
                                </Button>
                            </>
                        )}
                        {viewMode === "result" && (
                            <>
                                <Button
                                    disabled={!previousId}
                                    className={styles.iconButton}
                                    onClick={() => {
                                        if (previousId) {
                                            dispatch(PageActions.getContentInfo({content_id: previousId}))
                                            history.push(routes.lk.viewer(previousId))
                                        }
                                    }}
                                >
                                    <Previous />
                                </Button>
                                <Button
                                    disabled={!nextId}
                                    className={styles.iconButton}
                                    onClick={() => {
                                        if (nextId) {
                                            dispatch(PageActions.getContentInfo({content_id: nextId}))
                                            history.push(routes.lk.viewer(nextId))
                                        }
                                    }}>
                                    <Next />
                                </Button>
                            </>
                        )}

                    </Space>
                </div>
            </GridContainer>
        </div>
    )
}

export default ApproveBar;