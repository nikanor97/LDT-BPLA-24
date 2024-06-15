import * as React from 'react';
import Layout from '../../Modules/Layout/Layout';
import StatContainer from '@root/Components/StatContainer/StatContainer';
import DetectionsIcon from '../../Icons/Detections';
import ContentAfterDetectioncon from '../../Icons/ContentAfterDetection';
import ContentModerated from '../../Icons/ContentModerated';
import { useSelector } from 'react-redux';
import {PageState} from '../../../../../../../../Redux/types';
import styles from './Content.module.scss';
import useGetStatData from './Hooks/useGetStatData';


const Content = () => {
    const content = useSelector((state: PageState)  => state.Pages.LkProject.content.data);
    const data = useGetStatData();

    if (!content) return null;

    if (!data) return null;
    return (
        <Layout 
            items={[
                (
                    <StatContainer 
                        count={data.detected_count}
                        title="Всего обнаружений"
                        icon={<DetectionsIcon />}
                    />
                ),
                (
                    <StatContainer 
                        count={data.content_after_detection}
                        total={
                            <span className={styles.meta}>
                            /{data.content_count}
                            </span>
                        }
                        title="Прошли детекцию"
                        icon={<ContentAfterDetectioncon />}
                    />
                ),
                (
                    <StatContainer 
                        count={
                            data.content_moderated
                        }
                        total={
                            <span className={styles.meta}>
                            /{data.content_count}
                            </span>
                        }
                        title="Прошли модерацию"
                        icon={<ContentModerated />}
                    />
                )
            ]}
        />
    )
}
export default Content;