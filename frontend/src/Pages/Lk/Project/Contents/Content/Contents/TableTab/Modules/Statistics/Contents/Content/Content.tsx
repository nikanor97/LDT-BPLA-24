import * as React from 'react';
import Layout from '../../Modules/Layout/Layout';
import StatContainer from '@root/Components/StatContainer/StatContainer';
import HomeIcon from '../../Icons/Home';
import TimeIcon from '../../Icons/Timer';
import Tick from '../../Icons/Tick';
import { useSelector } from 'react-redux';
import {PageState} from '../../../../../../../../Redux/types';
import styles from './Content.module.scss';


const Content = () => {
    const data = useSelector((state: PageState) => state.Pages.LkProject.statistics.request.data);
    if (!data) return null;
    return (
        <Layout 
            items={[
                (
                    <StatContainer 
                        count={data.total_apartments}
                        title="Всего квартир"
                        icon={<HomeIcon />}
                    />
                ),
                (
                    <StatContainer 
                        count={
                            <>
                                {data.total_video_length_minutes}
                                {' '}
                                <span className={styles.timeMeta}>
                                мин
                                </span>
                            </>
                        }
                        title="Продолжительность видео"
                        icon={<TimeIcon />}
                    />
                ),
                (
                    <StatContainer 
                        count={
                            data.apartments_approved
                        }
                        total={
                            <span className={styles.meta}>
                            /{data.total_apartments}
                            </span>
                        }
                        title="Количество проверенных"
                        icon={<Tick />}
                    />
                )
            ]}
        />
    )
}
export default Content;