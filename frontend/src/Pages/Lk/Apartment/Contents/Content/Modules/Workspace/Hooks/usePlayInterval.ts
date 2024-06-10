import {useSelector} from 'react-redux';
import {PageState} from '../../../../../Redux/types';
import {Videosjs} from '@root/Types';


export const usePlayInterval = (player: Videosjs.Player | undefined) => {
    const playInterval = useSelector((state: PageState) => state.Pages.LkApartment.playInterval);
    if (!playInterval) return null;
    if (!player) return null;
    const duration = player.duration();
    const left = playInterval.start / duration * 100;
    const right = 100 - (playInterval.end / duration * 100);
    return {
        left,
        right,
        start: playInterval.start,
        end: playInterval.end
    }
}