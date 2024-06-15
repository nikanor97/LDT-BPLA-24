import * as React from 'react';
import Header from './Modules/Header/Header';
import TableTab from './Contents/TableTab/TableTab';
import UploadDrawer from './Modules/Header/Modules/UploadDrawer/UploadDrawer';


const Content = () => {
    return (
        <div>
            <Header />
            <TableTab />
            <UploadDrawer />
        </div>
    )
}

export default Content;