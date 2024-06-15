import * as React from 'react';
import {Result} from 'antd';

const Error = () => {
    return (
        <Result 
            status="500"
            title="Ошибка при получении данных"
        />
    )
}

export default Error;