import {Viewer} from '@root/Types';
import {StatusType} from '@root/Components/StatusTag/StatusTag';

export const getStatusText = (status: Viewer.Status) => {
    switch (status) {
        case 'created':
            return 'В обработке';
        case 'in_progress':
            return 'В работе';
        case 'approved':
            return 'Модерация выполнена';
        case 'declined':
            return 'Отклонен'
        case 'extracted':
            return 'Детекция выполнена'
        default:
            return 'Неизвестный'
    }
}

export const getStatusType = (status: Viewer.Status): StatusType => {
    switch (status) {
        case 'approved':
            return 'success';
        case 'declined':
            return 'declined';
        case 'extracted':
            return 'extracted';
        default:
            return 'default'
    }
}