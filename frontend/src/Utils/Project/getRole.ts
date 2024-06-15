import {Project} from '@root/Types'

export const getRole = (role: Project.Role) => {
    switch (role) {
        case 'author':
            return 'Автор';
        case 'verificator':
            return 'Верификатор';
        default:
            return null;
    }
}