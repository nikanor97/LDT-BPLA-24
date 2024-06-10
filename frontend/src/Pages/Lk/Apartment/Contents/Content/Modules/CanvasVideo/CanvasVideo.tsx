import React, {useRef, useEffect, useCallback, forwardRef, useImperativeHandle} from 'react';
import Constants from '@root/Data/Constants';
import videojs from 'video.js';
import {Videosjs} from '@types';
import styles from './CanvasVideo.module.scss';


type iCanvasVideo = {
    src: string;
    onProgress?: (player: Videosjs.Player) => any;
    onReady?: (player: Videosjs.Player) => any;
    onPlay?: (player: Videosjs.Player) => any;
    onPause?: (player: Videosjs.Player) => any;
    onLoaded?: (player: Videosjs.Player) => any; 
    onError?: (player: Videosjs.Player) => any; 
    width: number; //original
    height: number; //original
    scale: number;
    className?: string;
}

const CanvasVideo = forwardRef<Videosjs.Player | null | undefined, iCanvasVideo>((props, ref) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const videoContainer = React.useRef<HTMLDivElement>(null);
    const video = React.useRef<HTMLVideoElement | null>(null);
    const player = React.useRef<Videosjs.Player | null>(null);

    useImperativeHandle(ref, () => player.current ? player.current : undefined, [player.current])
    
    const playerInitialized = useCallback(() => {
        if (!player.current) return;
        props.onReady && props.onReady(player.current);
        requestAnimation();
        //@ts-ignore
        window.player = player.current;

        player.current.on('play', () => {
            if (player.current) {
                props.onPlay && props.onPlay(player.current)
            }
        })
        player.current.on('pause', () => {
            if (player.current) {
                props.onPause && props.onPause(player.current)
            }
        })
        player.current.on('loadeddata', (event:any) => {
            if (player.current) {
                props.onLoaded && props.onLoaded(player.current);
            }
        })
        player.current.on('error', (event:any) => {
            if (player.current) {
                props.onError && props.onError(player.current);
            }
        })
    }, []);
    
    const syncCanvas = useCallback(() => {
        if (!video.current) return;
        if (!canvasRef.current) return;
        const context = canvasRef.current.getContext('2d');
        if (!context) return;
        context.drawImage(video.current, 0, 0, props.width * props.scale, props.height * props.scale)
    }, [props.scale]);

    const requestAnimation = useCallback(() => {
        requestAnimationFrame(() => {
            syncCanvas()
            if (player.current) {
                if (!player.current.paused()) {
                    props.onProgress && props.onProgress(player.current);
                }
            }
            requestAnimation();
        })
    }, []);


    useEffect(() => {
        //создание экземпляра плеера и запись в рефы
        if (!videoContainer.current) return;
        if (player.current) return;

        const element = document.createElement("video");
        video.current = element;
        element.setAttribute("id",Constants.VIDEO_ID)
        videoContainer.current?.appendChild(element);
        
        player.current = videojs(
            element, 
            {
                preload: 'auto',
                sources: [{
                    src: props.src,
                    type: 'video/mp4'
                }],
                
                children: [
                    'MediaLoader',
                    'LoadingSpinner',
                    'ResizeManager'
                ]
            },
            playerInitialized
        );
    }, [])

    return (
        <div className={props.className}>
            <div 
                ref={videoContainer}
                className={styles.videoContainer}
            />
            <canvas 
                id="canvas" 
                ref={canvasRef}
                width={props.width * props.scale}
                height={props.height * props.scale}
            />
        </div>
    )
})

export default CanvasVideo;