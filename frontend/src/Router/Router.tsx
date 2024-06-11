import Pages from '@root/Pages';
import routes from '@root/routes';
import {Switch, Route, Redirect} from 'react-router-dom';
import PageRoute from '@root/Components/PageRoute/PageRoute';
import CheckRole from '@root/Containers/CheckRole/CheckRole';

const Router = () => {
    return (
        <Switch>
            <Route 
                path="/" 
                exact>
                <Pages.Index />
            </Route>
            <Route path={[
                routes.login,
                routes.registration
            ]}>
                <CheckRole 
                    error={<Redirect to={routes.lk.projects} />}
                    roles={['unauth']}>
                    <>
                        <PageRoute 
                            path={routes.login} 
                            exact 
                            Component={Pages.Login}
                        />
                        <PageRoute  
                            path={routes.registration} 
                            exact 
                            Component={Pages.Registration}
                        />
                    </>
                </CheckRole>
            </Route>
            <Route path={routes.lk.root}>
                <CheckRole 
                    error={<Pages.Page401 mode="unauth" />}
                    roles={['auth']}>
                    <Switch>
                        <PageRoute 
                            path={routes.lk.projects}
                            exact
                            Component={Pages.Lk.Projects}
                        />
                        <PageRoute 
                            path={routes.lk.project()}
                            exact
                            Component={Pages.Lk.Project}
                        />
                        <PageRoute 
                            path={routes.lk.apartment()}
                            exact
                            Component={Pages.Lk.Viewer}
                        />
                        <PageRoute 
                            path='*' 
                            Component={Pages.Page404}
                        />
                    </Switch>
                </CheckRole>
            </Route>
            <PageRoute 
                path='*' 
                Component={Pages.Page404}
            />
        </Switch>
    )
}


export default Router;