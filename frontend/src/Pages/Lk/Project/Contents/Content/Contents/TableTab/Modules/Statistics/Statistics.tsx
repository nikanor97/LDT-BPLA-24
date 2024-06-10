import React from 'react';
import {useSelector } from 'react-redux';
import {PageState} from '../../../../../../Redux/types';
import Content from './Contents/Content/Content';
import Loading from './Contents/Loading/Loading';


const Statistics = () => {
    const state = useSelector((state: PageState) => state.Pages.LkProject.statistics.request);

    if (state.data) {
        return <Content />
    }
    if (state.fetching) {
        return <Loading />;
    }
    return null;
}


export default Statistics;