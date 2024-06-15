import axios from 'axios';
import paths from './paths';


export default {
    getFile: () => axios.get(paths.getFile, {
        responseType: 'arraybuffer',
        
    })
}