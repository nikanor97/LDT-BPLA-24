import { useSelector } from 'react-redux';
import {PageState} from '../../../../../../../../../Redux/types';

const useGetStatData = () => {
    const content = useSelector((state: PageState)  => state.Pages.LkProject.content.data);
    if (!content) return null
    const data = {
        detected_count: 0,
        content_after_detection: 0,
        content_moderated: 0,
        content_count: content.length
    }

    content.forEach(item  => {
        if  (item.status === 'extracted') {
            data.content_after_detection  +=  1
        }
        if  (item.status === "approved" || item.status === "declined") {
            data.content_moderated  +=  1
        }
        data.detected_count += item.detected_count
    })

    return data;
}

export default  useGetStatData;