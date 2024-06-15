import React, {useRef, useEffect, useState} from 'react';
import styles from './Workspace.module.scss';
import CanvasPhoto from '../CanvasPhoto/CanvasPhoto';
import {usePhoto} from '../../Hooks/usePhoto';
import Markups from '../Markups/Markups';
import classnames from 'classnames'

const Workspace = () => {
    const photo = usePhoto();
    const container = useRef<HTMLDivElement>(null);
    const toolbar = useRef<HTMLDivElement>(null);
    const [scale, setScale] = useState<number>();

    const classes = {
        container: classnames(styles.container)
    }

    useEffect(() => {
        if (!container.current) return;
        if (!photo) return;
        const containerWidth = container.current.clientWidth;
        const containerHeight = container.current.clientHeight;
        const toolbarHeight = toolbar.current?.clientHeight || 0;
        
        const widthScale = containerWidth / photo.width;
        const heightScale = (containerHeight - toolbarHeight) / photo.height;
        setScale(Math.min(widthScale, heightScale, 1))
    }, [container, photo]);


    return (
        <div 
            ref={container}
            className={styles.wrapper}>
            <div  className={classes.container}>
                <div
                    className={styles.photoContainer} 
                    style={{position: 'relative'}}>
                    {
                        photo && scale !== undefined && (
                            <Markups
                                scale={scale}
                                width={photo.width}
                                height={photo.height}
                            />
                        )
                    }
                    {photo && scale !== undefined && (
                        <>
                            <CanvasPhoto 
                                src={`/api/static/photo/${photo.source_url}`}
                                width={photo.width}
                                height={photo.height}
                                scale={scale}
                                className={styles.video}
                            />
                        </>
                    )}
                </div>
            </div>
        </div>
        
    )
}

export default Workspace;