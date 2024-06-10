import * as React from 'react';
import {Form, Radio, Col, Row} from 'antd';
import styles from './Filters.module.scss';
import {Select} from '@root/Components/Controls';
import {useDispatch, useSelector} from 'react-redux';
import {Project} from '@root/Types';
import {PageState} from '../../../../../../Redux/types';
import {PageActions} from '../../../../../../Redux/Store';

const Filters = () => {
    const [form] = Form.useForm<Project.Statistics.Filters>();
    const data = useSelector((state: PageState) => state.Pages.LkProject.statistics.filters)
    const dispatch = useDispatch();

    return (
        <div>
            <Form<Project.Statistics.Filters>
                form={form}
                onValuesChange={() => {
                    setTimeout(() => {
                        const values = form.getFieldsValue();
                        dispatch(PageActions.setStatisticFilters(values));
                    }, 50)
                }}
                initialValues={data}
                className={styles.filtersForm}>
                <Row gutter={[28,0]}>
                    <Col>
                        <Form.Item name="mode">
                            <Radio.Group className={styles.radio}>
                                <Radio.Button value="home">
                                    Дом
                                </Radio.Button>
                                <Radio.Button value="floor">
                                    Этаж
                                </Radio.Button>
                            </Radio.Group>
                        </Form.Item>
                    </Col>
                    <Col>
                        <Form.Item 
                            shouldUpdate 
                            noStyle>
                            {(form) => {
                                const mode = form.getFieldValue('mode');
                                if (mode !== 'floor') return null;
                                return (
                                    <Form.Item 
                                        name="detalisation"
                                        label="Детализация">
                                        <Select 
                                            className={styles.select}
                                            placeholder="Выберите детализацию">
                                            <Select.Option value="mop">
                                                МОП
                                            </Select.Option>
                                            <Select.Option value="not_mop">
                                                Не МОП
                                            </Select.Option>
                                        </Select>
                                    </Form.Item>
                                )
                            }}
                        </Form.Item>
                    </Col>
                </Row>
            </Form>
        </div>
    )
}

export default Filters;