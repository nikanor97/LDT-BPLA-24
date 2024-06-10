import React, {useEffect} from 'react';
import Header from '@root/Modules/Header/Header';
import {App} from '@root/Types';
import HeaderInfo from './Contents/Content/Modules/HeaderInfo/HeaderInfo';
import HeaderContent from './Contents/Content/Modules/HeaderContent/HeaderContent';
import styles from './Apartment.module.scss';
import {useParams} from 'react-router-dom';
import {iParams} from './types';
import PageStateContainer from '@root/Containers/PageState/PageState';
import {Slice} from './Redux/Store';
import Saga from './Saga/ApartmentSaga';
import {useDispatch, useSelector} from 'react-redux';
import {PageActions} from './Redux/Store';
import ContentController from './Controllers/ContentController';
import {PageState} from './Redux/types';
import UploadDrawer from './Contents/Content/Modules/UploadDrawer/UploadDrawer';

const Apartment:App.Page = () => {
    const params = useParams<iParams>();
    const dispatch = useDispatch();
    const apartment = useSelector((state: PageState) => state.Pages.LkApartment.apartment.data)

    useEffect(() => {
        dispatch(PageActions.getApartment({apartId: params.apartId}))
        dispatch(PageActions.getVideos({apartment_id: params.apartId}))
    }, []);

    useEffect(() => {
        //@ts-ignore
        window.uploadFile = () => {
            dispatch(PageActions.openUploadDrawer());
        }
    }, []);

    useEffect(() => {
        if (apartment?.project_id === undefined) return;
        dispatch(PageActions.getLabels({project_id: apartment.project_id}))
    }, [apartment?.project_id]);

    return (
        <>
            <UploadDrawer />
            <ContentController />
        </>
    )
}

Apartment.getLayout = (page) => {
    return (
        <PageStateContainer params={[Slice, [Saga]]}>
            <div className={styles.page}>
                <Header 
                    className={styles.header}
                    Content={<HeaderContent />}
                    Logo={<HeaderInfo />}
                />
                <div className={styles.content}>
                    {page}
                </div>
            </div>
        </PageStateContainer>
    )
}

export default Apartment;