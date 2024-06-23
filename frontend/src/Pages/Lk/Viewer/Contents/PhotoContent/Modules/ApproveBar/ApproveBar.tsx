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
    const photoMarkup = useSelector((state:PageState)  => state.Pages.LkViewer.photoMarkup);
    const frames = useSelector((state: PageState) => state.Pages.LkViewer.content.data?.frames);
    const {previousId, nextId} = useGetPrevAndNextIds();
    const history  = useHistory();
    const dispatch = useDispatch();
    if (!data) return null;

    const goToNext  = ()  =>  {
        if (nextId) {
            dispatch(PageActions.getContentInfo({content_id: nextId}))
            dispatch(PageActions.erasePhotoMarkup());
            history.push(routes.lk.viewer(nextId))
        }
    };

    const goToPrevious = ()  =>  {
        if (previousId) {
            dispatch(PageActions.getContentInfo({content_id: previousId}))
            dispatch(PageActions.erasePhotoMarkup());
            history.push(routes.lk.viewer(previousId))
        }
    }

    return (
        <div className={styles.wrapper}>
            <GridContainer>
                <div>
                    <Space size={12}>
                        <Button
                            onClick={() => {
                                if (viewMode ===  "markup")  {
                                    const sendData = [{
                                        content_id: data.content_id,
                                        frame_id: frames ? frames[0].id : "0",
                                        new_markups: photoMarkup.newMarkups,
                                        deleted_markups: photoMarkup.changedMarkups
                                    }]
                                    dispatch(PageActions.sendPhotoMarkups({
                                        frames: sendData,
                                        onSuccess: () => dispatch(PageActions.setViewMode("result"))
                                    }))
                                } else {
                                    dispatch(PageActions.setViewMode("markup"))
                                }

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
                                            new_status: 'approved',
                                            onSuccess: goToNext
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
                                    onClick={goToPrevious}
                                >
                                    <Previous />
                                </Button>
                                <Button
                                    disabled={!nextId}
                                    className={styles.iconButton}
                                    onClick={goToNext}>
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