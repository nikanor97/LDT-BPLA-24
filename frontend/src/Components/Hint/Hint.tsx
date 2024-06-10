import React from "react";
import styles from "./Hint.module.scss";
import {Tooltip} from "antd";
import InfoIcon from "./Icons/InfoIcon";
import useGetSize from "./Hooks/useGetSize";
import {RenderFunction} from "antd/lib/tooltip";

type HintProps = {
    title: React.ReactNode | RenderFunction,
    width?: number,
    height?: number,
};

const Hint = (props: HintProps) => {
    const {width, height} = useGetSize({
        width: props.width,
        height: props.height
    });
    const {title} = props;

    return (
        <Tooltip 
            title={title}
            className={styles.hintTooltip}>
            <div
                className={styles.buttonHint}
                style={{
                    width,
                    height
                }}>
                <InfoIcon />
            </div>
        </Tooltip>
    );
};

export default Hint;
