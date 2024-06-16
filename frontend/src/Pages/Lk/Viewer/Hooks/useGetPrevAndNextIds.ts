import findAdjacentId from '@root/Pages/Lk/Viewer/Utils/findAdjasentId';
import {PageState} from '../Redux/types';
import { useSelector } from 'react-redux';

type ReturnValues = {
    previousId: string | null,
    nextId: string  | null
}

const useGetPrevAndNextIds = (): ReturnValues => {
    const currentId = useSelector((state: PageState) => state.Pages.LkViewer.content.data?.info?.content_id);
    const contentIds = useSelector((state: PageState) => state.Pages.LkViewer.content_ids.data);
    let previousId: string | null = null;
    let nextId: string | null = null;
    if (currentId && contentIds && contentIds.length > 0) {
        previousId = findAdjacentId(contentIds, currentId, "previous");
        nextId = findAdjacentId(contentIds, currentId, "next");
    }

    return {
        previousId,
        nextId
    }
}

export default useGetPrevAndNextIds;