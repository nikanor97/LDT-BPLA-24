import {useSelector} from "react-redux";
import {PageState} from '../../../Redux/types';

export const useFrame = () => {
    const frames = useSelector((state:PageState) => state.Pages.LkViewer.content.data?.frames)
    if (!frames) return null;
    return frames[0];

    
}