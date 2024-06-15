import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import reportWebVitals from './reportWebVitals';
import {BrowserRouter as Router} from 'react-router-dom';
import {ConfigProvider} from 'antd';
import {Provider} from 'react-redux';
import store from './Redux/store';
import './index.scss';
//@ts-ignore
import vars from './_variables.scss'

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
    <Provider store={store}>
        <ConfigProvider theme={{
            token: {
                colorPrimary: vars.primaryColor
            }
        }}>
            <Router>
                <App />
            </Router>
        </ConfigProvider>
    </Provider>
);
reportWebVitals();
