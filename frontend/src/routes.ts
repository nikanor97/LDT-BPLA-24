
export default {
    main: '/',
    login: '/login',
    registration: '/registration',
    lk: (() => {
        const prefix = '/lk'
        return {
            root: prefix,
            projects: `${prefix}/projects`,
            project: (pid: string = ':projectId') => `${prefix}/projects/${pid}`,
            //TODO Изменить нв viewer
            apartment: (aid: string = ':apartId') => `${prefix}/apartments/${aid}`
        }
    })()
}