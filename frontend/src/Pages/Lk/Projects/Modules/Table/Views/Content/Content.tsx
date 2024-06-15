import * as React from 'react';
import Table from '@root/Components/Table/Table';
import {useColumns} from '../../Hooks/useColumns';
import styles from './Content.module.scss';
import {useHistory} from 'react-router-dom';
import routes from '@root/routes';
import {useData} from '../../../../Hooks/useData';

const Content = () => {
    const columns = useColumns();
    const history = useHistory();
    const items = useData();

    if (!items) return null;

    return (
        <div className={styles.wrapper}>
            <Table
                columns={columns}
                dataSource={items}
                rowKey={(record) => record.id}
                pagination={false}
                onRow={(item) => {
                    return {
                        onClick: () => {
                            history.push(routes.lk.project(item.id))
                        }
                    }
                }}
            />
        </div>
    )
}


export default Content;