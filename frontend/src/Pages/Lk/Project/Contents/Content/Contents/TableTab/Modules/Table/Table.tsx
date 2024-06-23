import * as React from 'react';
import Table from '@root/Components/Table/Table';
import { useDispatch, useSelector } from 'react-redux';
import {PageState} from '../../../../../../Redux/types';
import {useColumns} from './Hooks/useColumns';
import styles from './Table.module.scss';
import {useHistory} from 'react-router-dom';
import routes from '@root/routes';
import { PageActions } from '@root/Pages/Lk/Project/Redux/Store';
import { Photo, Video } from '@root/Types';

const TableModule = () => {
    const data = useSelector((state:PageState) => state.Pages.LkProject.content.data);
    const columns = useColumns();
    const history = useHistory();
    const selectedContent = useSelector((state:PageState)  => state.Pages.LkProject.selectedContent);
    const dispatch = useDispatch();

    if (!data) return null;

    const rowSelection = {
        selectedRowKeys: selectedContent,
        onChange: (selectedRowKeys: React.Key[]) => { 
            dispatch(PageActions.setSelectedContent(selectedRowKeys));
        },
        getCheckboxProps: (record: Video.Item | Photo.Item) => {
            return ({
                name: record.content_id,
            });
        },
    };

    return (
        <div className={styles.wrap}>
            <Table 
                dataSource={data}
                pagination={false}
                columns={columns}
                className={styles.content}
                rowKey={(record) => record.content_id}
                rowSelection={rowSelection}
                onRow={(record) => {
                    return {
                        onClick: () => {
                            history.push(routes.lk.viewer(record.content_id))
                        }
                    }
                }}
            />
        </div>
    )
}

export default TableModule;