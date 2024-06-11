import {TableProps} from "antd"
import {Content} from '@root/Types';
import moment from "moment";
import StatusTag from "@root/Components/StatusTag/StatusTag";
import {getStatusText, getStatusType} from '@root/Utils/Viewer/getStatus';

type Columns = TableProps<Content.Item>['columns']


export const useColumns = ():Columns => {
    return [
        {
            title: 'Название',
            dataIndex: 'name'
        },
        {
            title: 'Дата загрузки',
            dataIndex: 'created_at',
            render: (value) => {
                const momentValue = moment(value);
                return momentValue.format('DD.MM.YYYY')
            }
        },
        {
            title: 'Обнаружено объектов',
            dataIndex: 'detected_objects',
        },
        {
            title: 'Статус',
            dataIndex: 'status',
            render: (status: Content.Status) => {
                return (
                    <StatusTag 
                        type={getStatusType(status)}
                        text={getStatusText(status)}
                    />
                )
            }
        },
    ]
}