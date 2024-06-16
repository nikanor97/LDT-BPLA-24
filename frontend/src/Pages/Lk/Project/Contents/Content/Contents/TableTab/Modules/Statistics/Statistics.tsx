import React from 'react';
import {useSelector } from 'react-redux';
import {PageState} from '../../../../../../Redux/types';
import Content from './Contents/Content/Content';
import Loading from './Contents/Loading/Loading';


const Statistics = () => {
    const content = useSelector((state: PageState)  => state.Pages.LkProject.content);

    if (content.data) {
        return <Content />
    }
    if (content.fetching) {
        return <Loading />;
    }
    return null;
}


export default Statistics;