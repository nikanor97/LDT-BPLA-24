import {useSelector} from "react-redux"
import {PageState} from '../../../Redux/types';


export const useVideo = () => {
    const data = useSelector((state:PageState) => state.Pages.LkApartment.videos.data?.video);
    if (data) return data;
    return null;
}
