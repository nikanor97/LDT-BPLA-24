import * as React from 'react';
import Table from '@root/Components/Table/Table';
import { useSelector } from 'react-redux';
import {PageState} from '../../../../../../Redux/types';
import {useColumns} from './Hooks/useColumns';
import styles from './Table.module.scss';
import {useHistory} from 'react-router-dom';
import routes from '@root/routes';

const TableModule = () => {
    const data = useSelector((state:PageState) => state.Pages.LkProject.content.data);
    const columns = useColumns();
    const history = useHistory();
    if (!data) return null

    return (
        <div className={styles.wrap}>
            <Table 
                dataSource={data}
                pagination={false}
                columns={columns}
                className={styles.content}
                rowKey={(record) => record.id}
                onRow={(record) => {
                    return {
                        onClick: () => {
                            //TODO Изменить на пуш в viewer
                            history.push(routes.lk.apartment(record.id))
                        }
                    }
                }}
            />
        </div>
    )
}

export default TableModule;