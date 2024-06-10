import {Apartment} from '@root/Types';
import {StatusType} from '@root/Components/StatusTag/StatusTag';

export const getStatusText = (status: Apartment.Status) => {
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

export const getStatusType = (status: Apartment.Status): StatusType => {
    switch (status) {
        case 'approved':
            return 'success';
        default:
            return 'default'
    }
}