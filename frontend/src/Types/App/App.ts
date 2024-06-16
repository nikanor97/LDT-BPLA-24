

export type Page<T = any> = ((props:T) => JSX.Element) & {
    getLayout?: (page: JSX.Element) => JSX.Element;
}

export type children = null | JSX.Element;