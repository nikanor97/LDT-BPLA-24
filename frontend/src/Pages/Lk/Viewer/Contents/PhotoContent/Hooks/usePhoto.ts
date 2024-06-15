import {useSelector} from "react-redux"
import {PageState} from '../../../Redux/types';
import { Viewer } from "@root/Types";


export const usePhoto = () => {
    const data = useSelector((state:PageState) => state.Pages.LkViewer.content.data?.info);
    if (data && Viewer.isPhotoItem(data)) return data;
    return null;
}
