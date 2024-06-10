import * as React from 'react';
import Filters from '../../Modules/Filters/Filters';
import StatisticsController from '../../Modules/StatisticsController/StatisticsController';


const Content = () => {
    return (
        <div>
            <div>
                <Filters />
            </div>
            <StatisticsController />
        </div>
    )
}


export default Content;