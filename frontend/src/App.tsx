
import Router from './Router/Router';
import GetUser from '@root/Containers/GetUser/GetUser';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement
} from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);


function App() {
    return (
        <GetUser>
            <Router />
        </GetUser>
    )
}

export default App;
