type useGetSizeProps = {
    width: number | undefined,
    height: number | undefined
}

const useGetSize = (props: useGetSizeProps) => {
    const {width, height} = props;
    if (width === undefined || height === undefined) return {
        width: 16,
        height: 16
    };
    return {
        width,
        height
    };
};

export default useGetSize;
