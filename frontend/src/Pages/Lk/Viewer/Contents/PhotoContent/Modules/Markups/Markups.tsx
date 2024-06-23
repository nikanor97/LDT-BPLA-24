
import React, { useCallback, useEffect, useState } from 'react';
import styles from './Markups.module.scss';
import { useSelector, useDispatch } from 'react-redux';
import { PageState } from '../../../../Redux/types';
import { PageActions } from '../../../../Redux/Store';
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

type newMarkup = Omit<Markup, "confidence">;

const Markups = (props: iMarkups) => {
    const photo = usePhoto();
    const labels = useSelector((state: PageState) => state.Pages.LkViewer.labels.data);
    const frames = useSelector((state: PageState) => state.Pages.LkViewer.content.data?.frames);
    const newMarkups = useSelector((state: PageState) => state.Pages.LkViewer.photoMarkup.newMarkups)
    const canvas = React.useRef<HTMLCanvasElement>(null);
    const fabricRef = React.useRef<fabric.Canvas>();
    const frame = useFrame();
    const isShiftPressed = React.useRef(false);
    const selectedLabel  = useSelector((state: PageState)=> state.Pages.LkViewer.photoMarkup.selectedLabel);
    const dispatch = useDispatch();

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
        if (!fabricRef.current || !selectedLabel) return;

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
                stroke:  getDefaultColor(selectedLabel?.color),
                strokeWidth: 2,
                fill: `${getDefaultColor(selectedLabel?.color)}15`,
                // hasControls: true,
                // lockScalingX: false,
                // lockScalingY: false,
                // lockRotation: false,
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
                        coord_top_left_x: (rect.left && rect.left / props.scale) ?? 0,
                        coord_top_left_y: (rect.top && rect.top / props.scale) ?? 0,
                        coord_bottom_right_x: offsetX / props.scale,
                        coord_bottom_right_y: offsetY / props.scale,
                        label_id: selectedLabel?.id || "0",
                        frame_id: frame.id,
                        id: `${rect.left}${rect.top}${offsetX}${offsetY}${selectedLabel?.id}`
                    }
                    dispatch(PageActions.setPhotoNewMarkups([...newMarkups, recInfo]))
                }
            
            }
            rect = null;
        });

    }, [newMarkups, selectedLabel]);


    useEffect(()  => {
        if (!fabricRef.current || !labels) return;

        if (newMarkups.length > 0) {
            newMarkups.forEach((markup) => {
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
                    // hasControls: true,
                    // lockScalingX: false,
                    // lockScalingY: false,
                    // lockRotation: false,
                    strokeUniform: true,
                    data: markup.frame_id
                });
    
                fabricRef.current?.add(rect);
            });
        }
    }, [newMarkups])

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