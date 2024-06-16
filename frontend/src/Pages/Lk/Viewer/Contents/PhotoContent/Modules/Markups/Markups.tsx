import React, {useRef, useEffect} from 'react';
import styles from './Markups.module.scss';
import {useSelector} from 'react-redux';
import {PageState} from '../../../../Redux/types';
import {fabric} from 'fabric';
import { usePhoto } from '../../Hooks/usePhoto';
import { useFrame } from '../../Hooks/useFrame';
import {getDefaultColor} from '@root/Utils/Labels/getDefaultColor';

type iMarkups = {
    scale: number;
    width: number;
    height: number;
}

const Markups = (props: iMarkups) => {
    const photo = usePhoto();
    const labels = useSelector((state:PageState) => state.Pages.LkViewer.labels.data)
    const frames = useSelector((state:PageState) => state.Pages.LkViewer.content.data?.frames)
    const canvas = useRef<HTMLCanvasElement>(null);
    const fabricRef = useRef<fabric.Canvas>();
    const frame = useFrame();

    useEffect(() => {
        if (!canvas.current) return;
        const result = new fabric.Canvas(canvas.current)
        fabricRef.current = result;
    }, [])

    useEffect(() => {
        if (!fabricRef.current) return;
        if (!labels) return;
        if (!frame) return;
        frame.markups.forEach((markup) => {
            const label = labels[markup.label_id];
            const width = Math.abs(markup.coord_bottom_right_x - markup.coord_top_left_x) * props.scale;
            const height = Math.abs(markup.coord_bottom_right_y - markup.coord_top_left_y) * props.scale;
            const top = markup.coord_top_left_y * props.scale;
            const left = markup.coord_top_left_x * props.scale;
            const color = getDefaultColor(label.color);
            
            const Group = new fabric.Group([
                new fabric.Rect({
                    top: 16,
                    left:0,
                    width: width,
                    height: height,
                    stroke: color,
                    strokeWidth: 1,
                    fill: `${color}15`,
                    selectable: false
                }),
                new fabric.Text(`${label.name} ${Math.floor(markup.confidence * 100)}%`, {
                    width,
                    height: 24,
                    left: 0,
                    top: top < 16 ? height + 16: 0,
                    fontSize: 14,
                    backgroundColor: color,                    
                })
            ], {
                selectable: false,
                top: top - 16,
                left
            })
            fabricRef.current?.add(Group);
        })
    }, [])

    useEffect(() => {
        fabricRef.current?.setWidth(props.width * props.scale)
        fabricRef.current?.setHeight(props.height * props.scale)
    }, [props.scale])

    if (!photo) return null;
    if (!labels) return null;
    if (!frames) return null;

    return (
        <div className={styles.wrapper}>
            <canvas 
                ref={canvas}
                width={props.width * props.scale}
                height={props.height * props.scale}
            />
        </div>
    )
}

export default Markups;