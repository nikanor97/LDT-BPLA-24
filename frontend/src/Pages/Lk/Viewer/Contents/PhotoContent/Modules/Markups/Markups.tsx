
import React, { useCallback, useEffect, useState } from 'react';
import styles from './Markups.module.scss';
import { useSelector } from 'react-redux';
import { PageState } from '../../../../Redux/types';
import { fabric } from 'fabric';
import { usePhoto } from '../../Hooks/usePhoto';
import { useFrame } from '../../Hooks/useFrame';
import { getDefaultColor } from '@root/Utils/Labels/getDefaultColor';
import { Markup } from '@root/Types/Photo/Frames';

type iMarkups = {
    scale: number;
    width: number;
    height: number;
}

type newMarkup = Omit<Markup, "id" | "confidence">;

const Markups = (props: iMarkups) => {
    const photo = usePhoto();
    const labels = useSelector((state: PageState) => state.Pages.LkViewer.labels.data);
    const frames = useSelector((state: PageState) => state.Pages.LkViewer.content.data?.frames);
    const canvas = React.useRef<HTMLCanvasElement>(null);
    const fabricRef = React.useRef<fabric.Canvas>();
    const frame = useFrame();
    const [drawnRectangles, setDrawnRectangles] = useState<fabric.Rect[]>([]);
    const isShiftPressed = React.useRef(false);

    const [recsInfo, setRecsInfo] = useState<newMarkup[]>([])

    useEffect(() => {
        if (!canvas.current) return;

        const result = new fabric.Canvas(canvas.current, {
            isDrawingMode: false // Disable default drawing mode
        });
        fabricRef.current = result;
    }, [])

    const handleKeyDown = (event: KeyboardEvent) => {
        if (event.key === 'Shift') {
            isShiftPressed.current = true;
        }
    };

    const handleKeyUp = (event: KeyboardEvent) => {
        if (event.key === 'Shift') {
            isShiftPressed.current = false;
        }
    }

    useEffect(() => {
        document.addEventListener('keydown', handleKeyDown);
        document.addEventListener('keyup', handleKeyUp);

        return () => {
            document.removeEventListener('keydown', handleKeyDown);
            document.removeEventListener('keyup', handleKeyUp);
        };
    }, [handleKeyDown, handleKeyUp]);

    useEffect(() => {
        if (!fabricRef.current) return;

        let rect: fabric.Rect | null = null;

        fabricRef.current.on('mouse:down', (event: fabric.IEvent) => {

            if (!isShiftPressed.current) return;
            const mouseEvent = event.e as MouseEvent;
            const { offsetX, offsetY } = mouseEvent;
            rect = new fabric.Rect({
                left: offsetX,
                top: offsetY,
                width: 0,
                height: 0,
                stroke: 'black',
                strokeWidth: 2,
                fill: 'transparent',
                hasControls: true,
                lockScalingX: false,
                lockScalingY: false,
                lockRotation: false,
                strokeUniform: true,
            });
        });

        fabricRef.current.on('mouse:move', (event: fabric.IEvent) => {
            if (!rect) return;
            if (!isShiftPressed.current) return;
            const mouseEvent = event.e as MouseEvent;
            const { offsetX, offsetY } = mouseEvent;
            rect.set({
                width: offsetX - (rect.left ?? 0), // Добавляем проверку на существование rect.left
                height: offsetY - (rect.top ?? 0) // Добавляем проверку на существование rect.top
            });
        });

        fabricRef.current.on('mouse:up', (event: fabric.IEvent) => {
            if (!isShiftPressed.current) return;
            const mouseEvent = event.e as MouseEvent;
            const { offsetX, offsetY } = mouseEvent;
            if (rect) {
                if (frame) {
                    const recInfo: newMarkup  = {
                        coord_top_left_x: rect.left ?? 0,
                        coord_top_left_y: rect.top ?? 0,
                        coord_bottom_right_x: offsetX,
                        coord_bottom_right_y: offsetY,
                        label_id: "fff",
                        frame_id: frame.id,
                
                    }
                    setRecsInfo([...recsInfo, recInfo])
                }

                console.log(recsInfo);
            
                setDrawnRectangles([...drawnRectangles, rect]);
            }
            rect = null;
        });

    }, [drawnRectangles]);

    useEffect(()  => {
        if (drawnRectangles) {
            drawnRectangles.forEach((rect)  => {
                fabricRef.current?.add(rect);
            })
        }
    }, [drawnRectangles])

    useEffect(() => {
        if (!fabricRef.current || !labels || !frame) return;

        frame.markups.forEach((markup) => {
            const label = labels[markup.label_id];
            const width = Math.abs(markup.coord_bottom_right_x - markup.coord_top_left_x) * props.scale;
            const height = Math.abs(markup.coord_bottom_right_y - markup.coord_top_left_y) * props.scale;
            const top = markup.coord_top_left_y * props.scale;
            const left = markup.coord_top_left_x * props.scale;
            const color = getDefaultColor(label.color);

            const rect = new fabric.Rect({
                top: top,
                left: left,
                width: width,
                height: height,
                stroke: color,
                strokeWidth: 2,
                fill: `${color}15`,
                hasControls: true,
                lockScalingX: false,
                lockScalingY: false,
                lockRotation: false,
                strokeUniform: true,
                data: frame.id
            });

            fabricRef.current?.add(rect);
        });
    }, [labels, frame, props.scale]);

    useEffect(() => {
        if (fabricRef.current) {
            fabricRef.current.setWidth(props.width * props.scale);
            fabricRef.current.setHeight(props.height * props.scale);
        }
    }, [props.scale]);

    if (!photo || !labels || !frames) return null;

    return (
        <div className={styles.wrapper}>
            <canvas
                ref={canvas}
                width={props.width * props.scale}
                height={props.height * props.scale}
            />
        </div>
    );
}

export default Markups;