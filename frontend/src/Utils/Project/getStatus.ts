import {Project} from '@root/Types';
import {StatusType} from '@root/Components/StatusTag/StatusTag';

export const getStatusText = (status: Project.Status) => {
    switch (status) {
        case 'created':
            return 'Создан';
        case 'in_progress':
            return 'В работе';
        case 'finished':
            return 'Проверен';
        default:
            return 'Неизвестный'
    }
}

export const getStatusType = (status: Project.Status): StatusType => {
    switch (status) {
        case 'finished':
            return 'success';
        default:
            return 'default'
    }
}