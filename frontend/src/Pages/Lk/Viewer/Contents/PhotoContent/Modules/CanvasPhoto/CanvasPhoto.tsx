import React from 'react';

type iCanvasPhoto = {
    src: string;
    width: number; //original
    height: number; //original
    scale: number;
    className?: string;
}

const CanvasPhoto = (props: iCanvasPhoto) => {
    return (
        <div className={props.className}>
            <img 
                id="canvas" 
                src={props.src}
                alt="img"
                width={props.width * props.scale}
                height={props.height * props.scale}
            />
        </div>
    )
}

export default CanvasPhoto;