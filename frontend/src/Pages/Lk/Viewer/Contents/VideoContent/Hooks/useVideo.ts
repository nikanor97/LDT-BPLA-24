import {useSelector} from "react-redux"
import {PageState} from '../../../Redux/types';
import { Viewer } from "@root/Types";


export const useVideo = () => {
    const data = useSelector((state:PageState) => state.Pages.LkViewer.content.data?.info);
    if (data && Viewer.isVideoItem(data)) return data;
    return null;
}
