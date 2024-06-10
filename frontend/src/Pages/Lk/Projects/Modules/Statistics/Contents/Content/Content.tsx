import * as React from 'react';
import Layout from '../../Modules/Layout/Layout';
import StatContainer from '@root/Components/StatContainer/StatContainer';
import HomeIcon from '../../Icons/Home';
import VideoIcon from '../../Icons/Youtube';
import Tick from '../../Icons/Tick';
import { useSelector } from 'react-redux';
import {PageState} from '../../../../Redux/types';
import styles from './Content.module.scss';
import StatLineContainer from '@root/Components/StatLineContainer/StatLineContainer';


const Content = () => {
    const data = useSelector((state: PageState) => state.Pages.LkProjects.statistics.data);
    if (!data) return null;
    return (
        <Layout 
            items={[
                (
                    <StatLineContainer title='Загруженные данные' count1={2} count2={3} name1='Видео' name2='Видео' />
                ),
                (
                    <StatContainer 
                        title="Всего видео"
                        count={data.total_videos}
                        icon={<VideoIcon />}
                    />
                ),
                (
                    <StatContainer 
                        title="Всего проверенных"
                        count={data.apartments_approved}
                        total={
                            <span className={styles.total}>
                                /{data.total_apartments}
                            </span>
                        }
                        icon={<Tick />}
                    />
                )
            ]}
        />
    )
}
export default Content;