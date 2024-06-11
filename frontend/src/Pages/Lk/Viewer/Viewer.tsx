import React, {useEffect} from 'react';
import Header from '@root/Modules/Header/Header';
import {App} from '@root/Types';
import HeaderInfo from './Contents/Content/Modules/HeaderInfo/HeaderInfo';
import styles from './Viewer.module.scss';
import {useParams} from 'react-router-dom';
import {iParams} from './types';
import PageStateContainer from '@root/Containers/PageState/PageState';
import {Slice} from './Redux/Store';
import Saga from './Saga/ViewerSaga';
import {useDispatch, useSelector} from 'react-redux';
import {PageActions} from './Redux/Store';
import ContentController from './Controllers/ContentController';
import {PageState} from './Redux/types';

const Viewer:App.Page = () => {
    const params = useParams<iParams>();
    const dispatch = useDispatch();
    const video  = useSelector((state: PageState)  => state.Pages.LkViewer.videos.data?.video)

    useEffect(() => {
        dispatch(PageActions.getApartment({apartId: params.apartId}))
        dispatch(PageActions.getVideos({apartment_id: params.apartId}))
    }, []);


    useEffect(() => {
        if (video?.project_id === undefined) return;
        dispatch(PageActions.getLabels({project_id: video.project_id}))
    }, [video?.project_id]);

    return (
        <ContentController />
    )
}

Viewer.getLayout = (page) => {
    return (
        <PageStateContainer params={[Slice, [Saga]]}>
            <div className={styles.page}>
                <Header 
                    className={styles.header}
                    Logo={<HeaderInfo />}
                />
                <div className={styles.content}>
                    {page}
                </div>
            </div>
        </PageStateContainer>
    )
}

export default Viewer;