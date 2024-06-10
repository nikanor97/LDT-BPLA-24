import * as React from 'react';
import {useSelector} from 'react-redux';
import {PageState} from '../Redux/types';
import Loading from '../Contents/Loading/Loading'
import Error from '../Contents/Error/Error'
import Content from '../Contents/Content/Content'

const ContentController = () => {
    const state = useSelector((state:PageState) => state.Pages.LkProject.getProject);
    
    if (state.fetching) return <Loading />;
    if (state.error) return <Error />;
    if (state.data) return <Content />;

    return null;
}


export default ContentController;