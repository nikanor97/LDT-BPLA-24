const {override, overrideDevServer, addWebpackAlias} = require('customize-cra');
const path = require('path');


//Логи прокси
const useProxyLog = true;

const offProxyLog = 'silent';
const onProxyLog = 'debug';
const proxyLog = useProxyLog ? onProxyLog : offProxyLog;
const aliases = {
    "@root": "./src",
    "@components": "./src/Components",
    "@routes": "./src/Routes/Routes.ts",
    "@layouts": "./src/Layouts/index.tsx",
    "@pages": "./src/Pages",
    "@assets": "./src/Assets",
    "@containers": "./src/Containers",
    "@utils": "./src/Utils",
    "@redux": "./src/Redux",
    "@store": "./src/Redux/store.ts",
    "@api": "./src/Api/index",
    "@sagas": "./src/Sagas/root.ts",
    "@types": "./src/Types",
    "@actions": "./src/Redux/actions.ts",
    "@modules": "./src/Modules"
};
const getAliasWebpack = () => {
    const result = {};
    Object
        .entries(aliases)
        .forEach(([key,pathName]) => {
            result[key] = path.resolve(__dirname, pathName);
        });
    return result;
};



module.exports = {
    webpack: override(
        addWebpackAlias(getAliasWebpack()),
    ),
    
    
    devServer: overrideDevServer( (config) => {
        return {
            ...config,
            proxy: [
                
                {
                    context: ['/api'],
                    target: 'http://localhost:7047/',
                    changeOrigin: true,
                    logLevel: proxyLog
                },
            ]
        };
    })
};