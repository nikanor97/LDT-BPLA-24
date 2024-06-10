import * as React from 'react';
import {PageState} from '../../../../../../Redux/types';
import {useSelector} from 'react-redux';
import HomeStats from '../HomeStats/HomeStats'
import FloorStats from '../FloorStats/FloorStats';


const StatisticsController = () => {
    const state = useSelector((state:PageState) => state.Pages.LkProject.statistics.filters);

    if (state.mode === 'floor') {
        return <FloorStats />
    } else {
        return <HomeStats />
    }
}


export default StatisticsController;