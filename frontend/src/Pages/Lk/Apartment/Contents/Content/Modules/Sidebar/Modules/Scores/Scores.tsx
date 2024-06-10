import React, {useEffect} from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {iParams} from '../../../../../../types';
import {PageActions} from '../../../../../../Redux/Store';
import {useParams} from 'react-router-dom';
import {PageState} from '../../../../../../Redux/types';
import Loading from './Contents/Loading/Loading';
import Content from './Contents/Content/Content';
import { useVideo } from '../../../../Hooks/useVideo';
import styles from './Scores.module.scss';

const Scores = () => {
    const dispatch = useDispatch();
    const params = useParams<iParams>();
    const state = useSelector((state: PageState) => state.Pages.LkApartment.sidebarScores);
    const video = useVideo();

    useEffect(() => {
        if (state.data) return;
        dispatch(PageActions.getApartmentScores({
            apartment_id: params.apartId
        }))
    }, []);

    if (!video) return null;

    if (video.status === 'created') {
        return (
            <div className={styles.empty}>
                Детекция выполняется. Результаты будут доступны позже...
            </div>
        )
    }
        
    if (state.fetching) return <Loading />
    if (state.data) return <Content />
    return null;
}

export default Scores;