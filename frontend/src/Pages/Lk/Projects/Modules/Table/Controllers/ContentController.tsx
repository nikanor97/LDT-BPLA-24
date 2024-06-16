import React from 'react';
import { useSelector } from 'react-redux';
import {PageState} from '../../../Redux/types';
import Content from '../Views/Content/Content';
import Loading from '../Views/Loading/Loading';
import Empty from '../../../../../../Components/TableEmpty/TableEmpty';
import {Alert} from 'antd';



const ContentController = () => {
    const state = useSelector((state:PageState) => state.Pages.LkProjects.projects);
    if (state.error) return (
        <Alert 
            type="error"
            closable={false}
            message="Ошибка при получении данных"
        />
    );
    if (state.data) {
        if (state.data.length) return <Content />;
        return <Empty text="У вас еще нет проектов" />
    }
    if (state.fetching) return <Loading />;
    return null;
}


export default ContentController;