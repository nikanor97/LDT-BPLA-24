import {Viewer} from '@root/Types';
import {StatusType} from '@root/Components/StatusTag/StatusTag';

export const getStatusText = (status: Viewer.Status) => {
    switch (status) {
        case 'created':
            return 'Создан';
        case 'in_progress':
            return 'В работе';
        case 'approved':
            return 'Проверен';
        case 'declined':
            return 'Отклонен'
        default:
            return 'Неизвестный'
    }
}

export const getStatusType = (status: Viewer.Status): StatusType => {
    switch (status) {
        case 'approved':
            return 'success';
        default:
            return 'default'
    }
}