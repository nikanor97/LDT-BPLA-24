import { useSelector } from "react-redux"
import {PageState} from '../../../../../../../Redux/types';



export const usePieData = () => {
    const filter = useSelector((state: PageState) =>  state.Pages.LkProject.statistics.filters.detalisation);
    const stats = useSelector((state: PageState) => state.Pages.LkProject.statistics.fullRequest.data);
    if (!stats) return null;

    if (filter === 'mop') {
        return {
            wall: stats.avg_floor.wall,
            floor: stats.avg_floor.floor,
            ceil: stats.avg_floor.ceiling
        }
    } else {
        return {
            wall: stats.avg_floor.mop_wall,
            floor: stats.avg_floor.mop_floor,
            ceil: stats.avg_floor.mop_ceiling
        }   
    }


}