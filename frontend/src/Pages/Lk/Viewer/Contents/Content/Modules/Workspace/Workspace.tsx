import React, {useRef, useEffect, useState, useCallback} from 'react';
import styles from './Workspace.module.scss';
import CanvasVideo from '../CanvasVideo/CanvasVideo';
import {useVideo} from '../../Hooks/useVideo';
import {CaretRightOutlined, PauseOutlined, LoadingOutlined, LeftOutlined, RightOutlined, DoubleLeftOutlined, DoubleRightOutlined} from '@ant-design/icons'
import {Videosjs} from '@root/Types';
import {getTimeInMinute} from '@root/Utils/Date/NormilizeTime';
import Markups from '../Markups/Markups';
import classnames from 'classnames'
import errImg from './Img/Noimage.png';
import {Alert, Tooltip} from 'antd';
import { useNextFrame } from './Hooks/useNextFrame';
import { usePrevFrame } from './Hooks/usePrevFrame';
import { useDispatch } from 'react-redux';
import {PageActions} from '../../../../Redux/Store';
import { HotKeys } from "react-hotkeys";
import {ShortcutNames} from './Data/Shortcuts';
import { useNextMarkupFrame } from './Hooks/useNextMarkupFrame';
import { usePrevMarkupFrame } from './Hooks/usePrevMarkupFrame';
import { usePlayInterval } from './Hooks/usePlayInterval';
import {ceil} from 'lodash';

const Workspace = () => {
    const video = useVideo();
    const [player, setPlayer] = useState<Videosjs.Player>();
    const [loading, setLoading] = useState(true);
    const [loaded, setLoaded] = useState(false);
    const [error, setError] = useState(false);
    const [played, setPlayed] = useState(false);

    const [progress, setProgress] = useState(0);
    const container = useRef<HTMLDivElement>(null);
    const toolbar = useRef<HTMLDivElement>(null);
    const [scale, setScale] = useState<number>();
    const nextFrame = useNextFrame(player, setProgress);
    const prevFrame = usePrevFrame(player, setProgress);
    const nextMarkupFrame = useNextMarkupFrame(player, setProgress);
    const prevMarkupFrame = usePrevMarkupFrame(player, setProgress);
    const dispatch = useDispatch();
    const playInterval = usePlayInterval(player);

    const classes = {
        container: classnames(styles.container, {
            [styles.containerLoaded]: loaded
        })
    }

    const goTo = useCallback((time: number) => {
        if (!player) return;
        player.currentTime(time);
        setProgress(time);
    }, [player])
    
    const play = useCallback(() => {
        if (player) {
            player.play();
        }
    }, [player]);
    const pause = useCallback(() => {
        if (player) {
            player.pause();
        }
    }, [player]);

    const togglePlay = useCallback(() => {
        if (!player) return;
        if (player.paused()) play()
        else pause()
    }, [play, played, pause]);

    useEffect(() => {
        if (!container.current) return;
        if (!video) return;
        const containerWidth = container.current.clientWidth;
        const containerHeight = container.current.clientHeight;
        const toolbarHeight = toolbar.current?.clientHeight || 0;
        
        const widthScale = containerWidth / video.width;
        const heightScale = (containerHeight - toolbarHeight) / video.height;
        setScale(Math.min(widthScale, heightScale, 1))
        
    }, [container, video, loaded]);

    useEffect(() => {
        if (!playInterval) return;
        goTo(ceil(playInterval.start, 4));
        if (playInterval.start !== playInterval.end) {
            play();
        }
    }, [playInterval?.start, playInterval?.end, goTo]);

    useEffect(() => {
        if (!playInterval) return;

        if (playInterval.end <= progress) {
            dispatch(PageActions.setPlayInterval(null))
            player?.pause();
        }
    }, [progress])

    return (
        <HotKeys 
            className={styles.shortcuts}
            handlers={{
                [ShortcutNames.NEXT_FRAME]: nextFrame,
                [ShortcutNames.NEXT_MARKUP_FRAME]: nextMarkupFrame,
                [ShortcutNames.PREV_FRAME]: prevFrame,
                [ShortcutNames.PREV_MARKUP_FRAME]: prevMarkupFrame,
                [ShortcutNames.TOGGLE_PLAY]: togglePlay
            }}
            keyMap={{
                [ShortcutNames.NEXT_FRAME]: "right",
                [ShortcutNames.NEXT_MARKUP_FRAME]: ["t+right", "е+right"],
                [ShortcutNames.PREV_FRAME]: "left",
                [ShortcutNames.PREV_MARKUP_FRAME]: ["t+left", "е+left"],
                [ShortcutNames.TOGGLE_PLAY]: ["p","з"]
            }}>
            <div 
                ref={container}
                className={styles.wrapper}>
                <div  className={classes.container}>
                    {
                        loading && (
                            <div className={styles.loader}>
                                <LoadingOutlined/>
                            </div>
                        )
                    }
                    {
                        error && (
                            <img 
                                src={errImg}
                                alt='No data' 
                                className={styles.errImg}
                            />
                        )
                    }
                    <div
                        className={styles.videoContainer} 
                        style={{position: 'relative'}}>
                        {
                            video && loaded && scale !== undefined && (
                                <Markups 
                                    progress={progress}
                                    scale={scale}
                                    width={video.width}
                                    height={video.height}
                                />
                            )
                        }
                        {video && scale !== undefined && (
                            <>
                                <CanvasVideo 
                                    onReady={(player) => {
                                        setPlayer(player);
                                    }}
                                    onProgress={(player) => {
                                        setProgress(player.currentTime())
                                    }}
                                    src={`/api/v1/projects/video-file?video_id=${video.id}`}
                                    onPlay={() => {
                                        setPlayed(true)
                                    }}
                                    onError={() => {
                                        setLoaded(false)
                                        setLoading(false)
                                        setError(true);
                                    }}
                                    onPause={() => {
                                        setPlayed(false)
                                    }}
                                    onLoaded={(player) => {
                                        setLoading(false);
                                        setError(false)
                                        setLoaded(true);
                                        const duration = player.duration();
                                        const width = player.videoWidth();
                                        const height = player.videoHeight();
                                        dispatch(PageActions.updateVideoMeta({
                                            length_sec: duration
                                        }))
                                    }}
                                    width={video.width}
                                    height={video.height}
                                    scale={scale}
                                    className={styles.video}
                                />
                            </>
                        )}
                    </div>
                    {
                        loaded && (
                            <div 
                                ref={toolbar}
                                className={styles.toolbar}>
                                <div className={styles.toolbarBtns}>
                                    <Tooltip title="Предыдущий кадр c разметкой (T + Left)">
                                        <span 
                                            onClick={prevMarkupFrame}
                                            style={{fontSize: '16px'}}>
                                            <DoubleLeftOutlined />
                                        </span>
                                    </Tooltip>
                                    <Tooltip title="Предыдущий кадр (Left)">
                                        <span 
                                            onClick={prevFrame}
                                            style={{fontSize: '16px'}}>
                                            <LeftOutlined />
                                        </span>
                                    </Tooltip>
                                    {
                                        !played && (
                                            <Tooltip title="Смотреть (P)">
                                                <span onClick={play}>
                                                    <CaretRightOutlined />
                                                </span>
                                            </Tooltip>
                                        
                                        )
                                    }
                                    {
                                        played && (
                                            <Tooltip title="Пауза (P)">
                                                <span onClick={pause}>
                                                    <PauseOutlined />
                                                </span>
                                            </Tooltip>
                                        )
                                    }
                                    <Tooltip title="Следующий кадр (Right)">
                                        <span 
                                            onClick={nextFrame}
                                            style={{fontSize: '16px'}}>
                                            <RightOutlined />
                                        </span>
                                    </Tooltip>
                                    <Tooltip title="Следующий кадр с разметкой (T + Right)">
                                        <span 
                                            onClick={nextMarkupFrame}
                                            style={{fontSize: '16px'}}>
                                            <DoubleRightOutlined />
                                        </span>
                                    </Tooltip>
                                </div>

                    
                                <div className={styles.time}>
                                    {getTimeInMinute(progress)}
                                </div>
                                <div 
                                    onClick={(event) => {
                                        if (!video) return;
                                        if (!player) return;
                                        const clickX = event.pageX;
                                        const targetX = event.currentTarget.offsetLeft;
                                        const width = event.currentTarget.clientWidth;
                                        const result = (clickX - targetX) / width;
                                        goTo(result * video.length_sec);
                                    }}
                                    className={styles.track}>
                                    {
                                        video && (
                                            <div className={styles.thumb} 
                                                style={{
                                                    width: `${progress/video?.length_sec * 100}%`,
                                                }}
                                            />
                                        )
                                    }
                                    {
                                        playInterval && (
                                            <div 
                                                className={styles.playInterval}
                                                style={{
                                                    left: `${playInterval.left}%`,
                                                    right: `${playInterval.right}%`,
                                                }}
                                            />
                                        )
                                    }
                                </div>
                                { 
                                    video && (
                                        <div className={styles.time}>
                                            {getTimeInMinute(video.length_sec)}
                                        </div>
                                    )
                                }
                            </div>
                        )
                    }
                </div>
                {
                    error && (
                        <Alert 
                            className={styles.alertErr}
                            type="error"
                            description="Не удалось загрузить видео"
                        />
                    )
                }
            
            </div>
        </HotKeys>
        
    )
}

export default Workspace;