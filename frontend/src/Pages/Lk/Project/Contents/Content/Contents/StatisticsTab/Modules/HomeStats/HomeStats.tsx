import * as React from 'react';
import ChartContainer from '@root/Components/ChartContainer/ChartContainer';
import {Bar} from 'react-chartjs-2';
import {Row, Col} from 'antd';
import styles from './HomeState.module.scss';
import { useSelector } from 'react-redux';
import {PageState} from '../../../../../../Redux/types';


const HomeStats = () => {
    const data = useSelector((state:PageState) => state.Pages.LkProject.statistics.fullRequest.data);
    if (!data) return null;
    return (
        <div className={styles.wrapper}>
            <Row gutter={[0, 24]}>
                <Col span={24}>
                    <ChartContainer 
                        desc={<>По этажам</>}
                        title={<>Объекты с чистовой отделкой</>}>
                        <Bar 
                            
                            options={{
                                aspectRatio: 4.3,
                                
                                plugins: {
                                    legend: {
                                        display: false
                                    }
                                }

                            }}
                            data={{
                                labels: data.for_floor.finishing.map((item) => `${item.floor} этаж`),
                                datasets: [
                                    {
                                        label: 'Dataset 1',
                                        backgroundColor: [
                                            '#43AED1',
                                            '#CEDBFB'
                                        ],
                                        data: data.for_floor.finishing.map((item) => item.value)
                                    },
                                ],
                            }}
                        />
                    </ChartContainer>
                </Col>
                <Col span={24}>
                    <ChartContainer 
                        desc={<>По этажам</>}
                        title={<>Объекты без отделки</>}>
                        <Bar 
                            
                            options={{
                                aspectRatio: 4.3,
                                
                                plugins: {
                                    legend: {
                                        display: false
                                    }
                                }

                            }}
                            data={{
                                labels: data.for_floor.no_decoration.map((item) => `${item.floor} этаж`),
                                datasets: [
                                    {
                                        label: 'Dataset 1',
                                        backgroundColor: [
                                            '#43AED1',
                                            '#CEDBFB'
                                        ],
                                        data: data.for_floor.no_decoration.map((item) => item.value)
                                    },
                                ],
                            }}
                        />
                    </ChartContainer>
                </Col>
            </Row>
        </div>
    )
}

export default HomeStats;