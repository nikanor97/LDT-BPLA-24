import {Tooltip} from "antd";
import React from "react";

type EllipsisStringProps = {
  type: "component" | "string";
  text: string;
  length: number;
  tooltip: boolean
};

const ellipsisString = (props: EllipsisStringProps) => {
    const {type, text, length, tooltip} = props;
    const truncatedText = text.length > length ? `${text.slice(0, length)}...` : text;
  
    if (type === "component" && tooltip && text.length > length) return (
        <Tooltip overlay={text}>
            <span>
                {truncatedText}
            </span>
        </Tooltip>
    );
    if (type === "component") return (
        <span>
            {truncatedText}
        </span>
    );
    return truncatedText;
};

export default ellipsisString;
