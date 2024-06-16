import {TableProps, Tag} from "antd"
import {Content} from '@root/Types';
import moment from "moment";
import StatusTag from "@root/Components/StatusTag/StatusTag";
import {getStatusText, getStatusType} from '@root/Utils/Viewer/getStatus';

type Columns = TableProps<Content.Item>['columns']


export const useColumns = ():Columns => {
    return [
        {
            title: 'Название',
            dataIndex: 'name',
            key: 'content_id',
        },
        {
            title: 'Дата загрузки',
            dataIndex: 'created_at',
            key:  'content_id',
            render: (value) => {
                const momentValue = moment(value);
                return momentValue.format('DD.MM.YYYY')
            }
        },
        {
            title: 'Обнаружено объектов',
            dataIndex: 'detected_count',
            key: 'content_id',
        },
        {
            title: 'Тип файла',
            dataIndex: 'content_type',
            key: 'content_id',
            render: (content_type: Content.Item['content_type'])  =>  {
                if (content_type === "photo") {
                    return <Tag style={{backgroundColor: "#fff1df", border:  "1px solid #F3AF3D", color: "#ca8c13"}}>Фото</Tag>
                } else return <Tag style={{backgroundColor: "#e4f1f7", border:  "1px solid #43AED1", color: "#078fb1"}}>Видео</Tag>
            }
        },
        {
            title: 'Статус',
            dataIndex: 'status',
            key: 'content_id',
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