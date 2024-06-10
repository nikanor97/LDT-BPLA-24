import {useSelector} from 'react-redux';
import {PageState} from '../Redux/types';
import {groupBy} from 'lodash';

export const useData = () => {
    const data = useSelector((state:PageState) => state.Pages.LkProjects.projects.data);
    if (!data) return null;
    return data;
}