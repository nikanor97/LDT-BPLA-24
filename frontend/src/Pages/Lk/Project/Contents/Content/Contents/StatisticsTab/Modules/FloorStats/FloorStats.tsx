import * as React from 'react';
import {Row, Col} from 'antd';
import StatContainer from '@root/Components/StatContainer/StatContainer';
import ChartContainer from '@root/Components/ChartContainer/ChartContainer';
import Trash from '../../Icons/Trash';
import Rosetka from '../../Icons/Rosetka';
import Kitchen from '../../Icons/Kitchen';
import {Pie, Bar} from 'react-chartjs-2';
import styles from './FloorStats.module.scss';
import { useSelector } from 'react-redux';
import {PageState} from '../../../../../../Redux/types';
import { usePieData } from './Hooks/usePieData';


const FloorStats = () => {
    const data = useSelector((state:PageState) => state.Pages.LkProject.statistics.fullRequest.data);
    const pieData = usePieData();

    if (!pieData) return null;
    if (!data) return null;
    return (
        <div className={styles.wrapper}>
            <Row gutter={[16,24]}>
                <Col span={8}>
                    <StatContainer 
                        title="Мусор"
                        count={
                            data.avg_floor.trash_bool
                                ? (<span className={styles.textVal}>Присутствует</span>)
                                : (<span className={styles.textVal}>Отсутствует</span>)
                        }
                        icon={<Trash />}
                    />
                </Col>
                <Col span={8}>
                    <StatContainer 
                        title="Розетки"
                        count={data.avg_floor.switch_total}
                        icon={<Rosetka />}
                    />
                </Col>
                <Col span={8}>
                    <StatContainer 
                        title="Кухня"
                        count={data.avg_floor.kitchen_total}
                        icon={<Kitchen />}
                    />
                </Col>
                <Col span={8}>
                    <ChartContainer title={<>Пол</>}>
                        <Pie 
                            
                            options={{
                                aspectRatio: 2,
                                offset: 2,
                                plugins: {

                                    legend: {
                                        labels: {
                                            usePointStyle: true,
                                        },
                                        position: 'right'
                                    }
                                }
                            }}
                            data={{
                                labels: [
                                    'Черновая',
                                    'Чистовая',
                                    'Нет отделки'
                                ],
                                datasets: [
                                    {
                                        label: 'Значение в %',
                                        data: [
                                            pieData.wall.rough_decor * 100,
                                            pieData.wall.finishing_decor * 100,
                                            pieData.wall.no_decor * 100,
                                        ],
                                        backgroundColor: [
                                            '#FEDF89',
                                            '#43AED1',
                                            '#CEDBFB',
                                        ],
                                    },
                                ],
                            }}
                        />
                    </ChartContainer>
                </Col>
                <Col span={8}>
                    <ChartContainer title={<>Потолок</>}>
                        <Pie     
                            options={{
                                aspectRatio: 2,
                                offset: 2,
                                plugins: {

                                    legend: {
                                        labels: {
                                            usePointStyle: true,
                                        },
                                        position: 'right'
                                    }
                                }
                            }}
                            data={{
                                labels: [
                                    'Черновая',
                                    'Чистовая',
                                    'Нет отделки'
                                ],
                                datasets: [
                                    {
                                        label: 'Значение  в %',
                                        data: [
                                            pieData.ceil.rough_decor * 100,
                                            pieData.ceil.finishing_decor * 100,
                                            pieData.ceil.no_decor * 100,
                                        ],
                                        backgroundColor: [
                                            '#FEDF89',
                                            '#43AED1',
                                            '#CEDBFB',
                                        ],
                                    },
                                ],
                            }}
                        />
                    </ChartContainer>
                </Col>
                <Col span={8}>
                    <ChartContainer title={<>Стена</>}>
                        <Pie     
                            options={{
                                aspectRatio: 2,
                                offset: 2,
                                plugins: {
                                    legend: {
                                        labels: {
                                            usePointStyle: true,
                                        },
                                        position: 'right'
                                    }
                                }
                            }}
                            data={{
                                labels: [
                                    'Черновая',
                                    'Чистовая',
                                    'Нет отделки'
                                ],
                                datasets: [
                                    {
                                        label: 'Значение в %',
                                        data: [
                                            pieData.wall.rough_decor * 100,
                                            pieData.wall.finishing_decor * 100,
                                            pieData.wall.no_decor * 100,
                                        ],
                                        backgroundColor: [
                                            '#FEDF89',
                                            '#43AED1',
                                            '#CEDBFB',
                                        ],
                                    },
                                ],
                            }}
                        />
                    </ChartContainer>
                </Col>
                <Col span={24}>
                    <ChartContainer title={<>Встречаемость объектов</>}>
                        <Bar 
                            options={{
                                aspectRatio: 4,
                                plugins: {
                                    legend: {
                                        display: false
                                    }
                                }

                            }}
                            data={{
                                labels: ['Унитаз', 'Отделка окна', 'Установленная батарея', 'Двери', 'Раковина'],
                                datasets: [
                                    {
                                        label: 'Dataset 1',
                                        backgroundColor: [
                                            '#43AED1',
                                            '#D6BBFB',
                                            '#FEDF89',
                                            '#CEDBFB',
                                            '#36BFFA',
                                        ],
                                        data: [
                                            data.avg_floor.toilet_pct * 100,
                                            data.avg_floor.window_decor_pct * 100,
                                            data.avg_floor.radiator_pct * 100,
                                            data.avg_floor.doors_pct * 100,
                                            data.avg_floor.bathtub_pct * 100,
                                        ]
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

export default FloorStats;