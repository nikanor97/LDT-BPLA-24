import React, {useMemo} from 'react';
import usePageStore from '@root/Hooks/Redux/usePageStore';
import {useSelector} from 'react-redux';
import {PageStateContainer as PageState} from '@root/Redux/store';


type iPageStateContainer = {
    params: Parameters<typeof usePageStore>
    children: JSX.Element | JSX.Element[];
};
type AppState = PageState<unknown>;



const PageStateContainer = (props: iPageStateContainer) => {
    //Контейнер позволяет избежать рендеринг страницы до инициализации стейта
    // => хуки useEffect [] не сработают пока нет стейта => диспатчи не уйдут в никуда
    const {params} = props;
    const Slice = params[0];
    const state = useSelector((state:AppState) => state.Pages);
    usePageStore(...props.params);

    const isset = useMemo(() => {
        if (!state) return false;
        return Slice.name in state;
    }, [state, Slice]);
    if (isset) return (
        <>
            {props.children}
        </>
    );
    else return null;
};


export default PageStateContainer;