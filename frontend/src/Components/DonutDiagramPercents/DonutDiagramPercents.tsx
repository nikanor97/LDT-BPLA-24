import React from "react";
import {VictoryLabel, VictoryPie} from "victory";

type DonutDiagramPercentsProps = {
    totalCount: number,
    usedCount: number,
    color: string
}

export const DonutDiagramPercents = (props: DonutDiagramPercentsProps ) => {
    const getPercent = () => {
        const percent = props.usedCount * (100 / props.totalCount);
        if (!isFinite(percent)) return 0;
        return percent;
    };

    const percent = getPercent();
    
    const getData = (percent: number) => {
        return [
            {
                x: 1,
                y: percent
            }, 
            {
                x: 2,
                y: 100 - percent
            }
        ];
    };
    
    const data = getData(percent);
    return (
        <svg 
            viewBox="0 0 400 400" 
            width="100%" 
            height="100%">
            <VictoryPie
                standalone={false}
                width={400} 
                height={400}
                data={[
                    {
                        x: 1,
                        y: 100
                    }
                ]}
                innerRadius={120}
                labels={() => null}
                style={{
                    data: {
                        fill: "#B3B3B3"
                    }
                }}/>
            <VictoryPie
                standalone={false}
                animate={{duration: 1000}}
                width={400} 
                height={400}
                data={data}
                innerRadius={120}
                cornerRadius={25}
                labels={() => null}
                style={{
                    data: {
                        fill: ({datum}) => {
                            return datum.x === 1 ? props.color : "transparent";
                        }
                    }
                }}/>
            <VictoryLabel
                textAnchor="middle" verticalAnchor="middle"
                x={200} 
                y={200}
                text={`${Math.round(data[0].y)}%`}
                style={{
                    fontSize: 80,
                    fontFamily: "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,'Noto Sans',sans-serif,'Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol','Noto Color Emoji'",
                    fontWeight: 600,
                }}/>
        </svg>
    );
};
