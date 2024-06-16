import a1 from './Images/avatar1.svg';
import a2 from './Images/avatar2.svg';
import a3 from './Images/avatar3.svg';
import a4 from './Images/avatar4.svg';
import a5 from './Images/avatar5.svg';
import a6 from './Images/avatar6.svg';
import a7 from './Images/avatar7.svg';
import a8 from './Images/avatar8.svg';
import a9 from './Images/avatar9.svg';
import a10 from './Images/avatar10.svg';
import a11 from './Images/avatar11.svg';
import a12 from './Images/avatar12.svg';
import {sum, round} from 'lodash';

const images = [
    a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12
]

export const getUserAvatar = (uid: string) => {
    const lettersSum = sum(
        uid
            .split('')
            .map((letter) => letter.charCodeAt(0))
    )
    const ost = lettersSum % 100;
    const resultIndex = round((ost / 100) * (images.length - 1))
    return images[resultIndex];
}