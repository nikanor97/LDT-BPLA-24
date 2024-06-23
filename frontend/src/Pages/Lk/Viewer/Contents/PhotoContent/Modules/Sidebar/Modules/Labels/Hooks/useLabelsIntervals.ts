import {LabelIntervals} from '../types';
import {useFramesByLabels} from "./useFramesByLabels"

const eraseInterval = (item: LabelIntervals) => {
    item.start = null;
    item.current = null;
    item.buffer = [];
}

export const useLabelsIntervals = () => {
    const framesByLabels = useFramesByLabels();
    if (!framesByLabels) return null;
    return Object.values(framesByLabels)
        .map((label) => {
            const intervals = label
                .results
                .reduce((acc, labelData) => {
                    if (acc.start === null || acc.current === null) {
                    //Запись первого значения
                        
                        acc.buffer.push({
                            frame: labelData.frame,
                            markup: labelData.markup
                        })
                    } else {
                    //Значение в сторе уже есть

                        //Разрываем диапозон
                        acc.result.push({
                            start: acc.start,
                            end: acc.current,
                            results: acc.buffer
                        })
                        eraseInterval(acc);
                        

                    }
                    return acc;
                }, {
                    result: [],
                    current: null,
                    start: null,
                    buffer: [],
                    label: null,
                    framesCount: 0
                } as LabelIntervals)
            intervals.label = label.label;
            intervals.framesCount = label.results.length;
            if (intervals.start !== null && intervals.current !== null) {
                intervals.result.push({
                    end: intervals.current,
                    start: intervals.start,
                    results: intervals.buffer
                })
                eraseInterval(intervals);
            }

            return intervals;
        })
}