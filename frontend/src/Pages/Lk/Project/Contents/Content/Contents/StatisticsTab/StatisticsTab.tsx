import * as React from 'react';
import {PageState} from '../../../../Redux/types';
import Loading from './Contents/Loading/Loading';
import Content from './Contents/Content/Content';
import { useSelector } from 'react-redux';

const StatisticsTab = () => {
    const state = useSelector((state: PageState) => state.Pages.LkProject.statistics.fullRequest);
    if (state.fetching) return <Loading />;
    if (state.data) return <Content />;
    return null;
}

export default StatisticsTab;