import React, {useEffect} from 'react';

import { useDispatch, useSelector } from 'react-redux';
import {PageActions} from '../../Redux/Store';
import {PageState} from '../../Redux/types';
import Content from './Contents/Content/Content';
import Loading from './Contents/Loading/Loading';


const Statistics = () => {
    const dispatch = useDispatch();
    const state = useSelector((state: PageState) => state.Pages.LkProjects.statistics);

    useEffect(() => {
        dispatch(PageActions.getProjectStats());
    }, []);

    if (state.data) {
        return <Content />
    }
    if (state.fetching) {
        return <Loading />;
    }
    return null;
}


export default Statistics;