import React from 'react';
import {Route, RouteProps} from 'react-router-dom';
import {App} from '@types';
import Default from '@root/Layouts/Default/Default';

type iRoute = Omit<RouteProps, 'element' | 'component'> & {
    Component: App.Page;
}

const RouteModule = ({Component, ...rest}: iRoute) => {
    const getLayout = Component.getLayout || ((page: JSX.Element) => {
        return (
            <Default>
                {page}
            </Default>
        )
    })

    return (
        <Route {...rest}>
            {getLayout(React.createElement(Component))}
        </Route>
    )
}

export default RouteModule;