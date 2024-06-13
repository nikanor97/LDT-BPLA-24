import * as React from 'react';
import {TableProps} from "antd"
import {Project} from '@root/Types';
import moment from 'moment';
import styles from './styles.module.scss';
import StatusTag from '@root/Components/StatusTag/StatusTag';
import {getStatusText, getStatusType} from '@root/Utils/Project/getStatus'

type Columns = TableProps<Project.ItemFull>['columns']

export const useColumns = ():Columns => {

    return [
        {
            dataIndex: ['name'],
            title: 'Название',
            key: 'name'
        },
        {
            dataIndex: ['created_at'],
            title: 'Дата загрузки',
            key: 'created_at',
            render: (value: string) => {
                const momentVal = moment(value);
                return (
                    <div>
                        <div className={styles.date}>
                            {momentVal.format('DD.MM.YYYY')} {momentVal.format('HH:mm')}
                        </div>
                    </div>
                )
            }
        },
        {
            dataIndex: ["detected_count"],
            title: "Обнаружено объектов",
            key: "detected_count"
        },
        {
            dataIndex: ["msg_receiver"],
            title: "Контакт ответственного",
            key: "msg_receiver"
        },
        {
            title: 'Статус',
            dataIndex: ['status'],
            key: 'status',
            render: (value: Project.Status) => {
                return (
                    <StatusTag 
                        text={getStatusText(value)}
                        type={getStatusType(value)}
                    />
                )
            }
        },
    ]
}