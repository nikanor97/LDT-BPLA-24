
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
import { Transform } from 'fabric/fabric-impl';

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
    const newMarkups = useSelector((state: PageState) => state.Pages.LkViewer.photoMarkup.newMarkups);
    const changedMarkups = useSelector((state: PageState) => state.Pages.LkViewer.photoMarkup.changedMarkups)
    const sidebarMode = useSelector((state: PageState)  => state.Pages.LkViewer.viewMode);
    const canvas = React.useRef<HTMLCanvasElement>(null);
    const fabricRef = React.useRef<fabric.Canvas>();
    const frame = useFrame();
    const isShiftPressed = React.useRef(false);
    const selectedLabel  = useSelector((state: PageState)=> state.Pages.LkViewer.photoMarkup.selectedLabel);
    const dispatch = useDispatch();

    var deleteIcon = "data:image/svg+xml,%3C%3Fxml version='1.0' encoding='utf-8'%3F%3E%3C!DOCTYPE svg PUBLIC '-//W3C//DTD SVG 1.1//EN' 'http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd'%3E%3Csvg version='1.1' id='Ebene_1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' x='0px' y='0px' width='595.275px' height='595.275px' viewBox='200 215 230 470' xml:space='preserve'%3E%3Ccircle style='fill:%23F44336;' cx='299.76' cy='439.067' r='218.516'/%3E%3Cg%3E%3Crect x='267.162' y='307.978' transform='matrix(0.7071 -0.7071 0.7071 0.7071 -222.6202 340.6915)' style='fill:white;' width='65.545' height='262.18'/%3E%3Crect x='266.988' y='308.153' transform='matrix(0.7071 0.7071 -0.7071 0.7071 398.3889 -83.3116)' style='fill:white;' width='65.544' height='262.179'/%3E%3C/g%3E%3C/svg%3E";

    var img = document.createElement('img');
    img.src = deleteIcon;

    const deleteObject = (_: MouseEvent, transform: Transform) => {
        let target = transform.target;

        fabricRef.current?.remove(target);
        if (target.data.new) {
            dispatch(PageActions.deletePhotoNewMarkup(target.data.id));
        } else {
            dispatch(PageActions.deleteOldMarkups(target.data.id));
        }
        return true;
    }

    const renderIcon = (ctx: CanvasRenderingContext2D, left: number, top: number, styleOverride: any, fabricObject: fabric.Object) => {
        var size = 24;
        ctx.save();
        ctx.translate(left, top);
        ctx.rotate(fabric.util.degreesToRadians(fabricObject.angle ? fabricObject.angle : 0));
        ctx.drawImage(img, -size/2, -size/2, size, size);
        ctx.restore();
    }

    useEffect(() => {
        if (!canvas.current) return;
        fabric.Object.prototype.controls.deleteControl = new fabric.Control({
            x: 0.5,
            y: -0.4,
            offsetY: 16,
            cursorStyle: 'pointer',
            mouseUpHandler: deleteObject,
            render: renderIcon,
        });
        

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
                    lockScalingX: true,
                    lockScalingY: true,
                    lockRotation: true,
                    lockMovementX: true,
                    lockMovementY: true,
                    strokeUniform: true,
                    hasRotatingPoint: false,
                    data: {
                        frame_id: markup.frame_id,
                        label_id: markup.label_id,
                        id: markup.id,
                        new: true
                    }
                });
                const sameMarkup = fabricRef.current?.getObjects().filter((obj)  =>  obj.data?.id === markup.id);
                if (sameMarkup && sameMarkup.length === 0) fabricRef.current?.add(rect);
            });
        }
    }, [newMarkups])

    useEffect(() => {
        if (!fabricRef.current || !labels || !frame) return;

        frame.markups.forEach((markup) => {
            if (changedMarkups.includes(markup.id)) return null;
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
                lockScalingX: true,
                lockScalingY: true,
                lockRotation: true,
                lockMovementX: true,
                lockMovementY: true,
                strokeUniform: true,
                hasRotatingPoint: false,
                data: {
                    frame_id: frame.id,
                    label_id: markup.label_id,
                    id: markup.id,
                    new: false
                }
            });
            const sameMarkup = fabricRef.current?.getObjects().filter((obj)  =>  obj.data?.id === markup.id);
            if (sameMarkup && sameMarkup.length === 0) fabricRef.current?.add(rect);
        });
    }, [labels, frame, props.scale]);

    useEffect(() => {
        if (fabricRef.current) {
            fabricRef.current.setWidth(props.width * props.scale);
            fabricRef.current.setHeight(props.height * props.scale);
        }
    }, [props.scale]);

    useEffect(()  =>  {
        if (fabricRef.current) {
            if (sidebarMode === "markup") {
                fabricRef.current.getObjects().forEach((obj)  =>  {
                    obj.selectable = true;
                })
            } else {
                fabricRef.current.getObjects().forEach((obj)  =>  {
                    obj.selectable = false;
                })
            }
            fabricRef.current.discardActiveObject();
            fabricRef.current.renderAll();
        }
    }, [sidebarMode])

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