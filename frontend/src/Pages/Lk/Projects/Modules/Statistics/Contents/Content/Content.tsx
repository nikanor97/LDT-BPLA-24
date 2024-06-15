import * as React from 'react';
import Layout from '../../Modules/Layout/Layout';
import { useSelector } from 'react-redux';
import {PageState} from '../../../../Redux/types';
import StatLineContainer from '@root/Components/StatLineContainer/StatLineContainer';
import StatDonutContainer from '@root/Components/StatDonutContainer/StatDonutContainer';


const Content = () => {
    const data = useSelector((state: PageState) => state.Pages.LkProjects.statistics.data);
    if (!data) return null;
    return (
        <Layout 
            items={[
                (
                    <StatLineContainer
                        title='Загруженные данные'
                        count1={data.photo_count} 
                        count2={data.video_count}
                        name1='Фото'
                        name2='Видео' />
                ),
                (
                    <StatDonutContainer 
                        title="Фото с обнаружениями"
                        count={data.photo_with_det_count}
                        total={data.photo_count}
                        color='#F3AF3D'
                        hint='Количество фото с обнаруженными объектами: самолет, вертолет, БПЛА самолетного типа, БПЛА коптерного типа, птица и другие объекты'
                    />
                ),
                (
                    <StatDonutContainer 
                        title="Видео с обнаружениями"
                        count={data.video_with_det_count}
                        total={data.video_count}
                        color='#43AED1'
                        hint='Количество видео с обнаруженными объектами: самолет, вертолет, БПЛА самолетного типа, БПЛА коптерного типа, птица и другие объекты'
                    />
                )
            ]}
        />
    )
}
export default Content;