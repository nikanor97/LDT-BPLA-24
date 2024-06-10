import {Grid} from 'antd';
export type Breakpoint = 'xxl' | 'xl' | 'lg' | 'md' | 'sm' | 'xs';

const {useBreakpoint} = Grid;
type iBox = {
    visible: null | Breakpoint[] | boolean;
    hide: null | Breakpoint[];
    children: JSX.Element;
}

const useCurrentBreakpoint = ():Breakpoint => {
    const screens = useBreakpoint();
    return Object
        .entries(screens)
        .reduce((result, [key,value]) => {
            if (value) return key as Breakpoint;
            return result;
        }, 'xs' as Breakpoint);
};

const Box = (props: iBox) => {
    const {visible, hide, children} = props;
    const current = useCurrentBreakpoint();
    if (visible === true) return children;
    if (visible === false) return null;
    if (!visible && !hide) return children;
    if (visible) {
        if (visible.includes(current)) return children;
        else return null;
    }
    if (hide) {
        if (hide.includes(current))  return null;
        else return children;
    }
    return null;
};

Box.defaultProps = {
    visible: null,
    hide: null
};

export default Box;