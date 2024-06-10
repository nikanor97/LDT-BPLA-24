import React, {useMemo} from 'react';
import {useVideo} from '../../Hooks/useVideo';
import * as yup from 'yup';
import styles from './Geoposition.module.scss';
import GeoIcon from '../../Icons/Geoposition';

const Geoposition = () => {
    const video = useVideo();
    const parsedData = useMemo(() => {
        let parsed;
        if (!video) return null;
        try {
            parsed = JSON.parse(video.description)
            if (typeof parsed === 'string') parsed = JSON.parse(parsed);
            return parsed;
        } catch (ex) {
            return null
        }
    }, [video]);
    const coordinates = useMemo(() => {
        if (!parsedData) return null;
        const schema = yup.object({
            altitude: yup.number().required(),
            latitude: yup.number().required(),
            longitude: yup.number().required(),
        })
        try {
            return schema.validateSync(parsedData)
        } catch (ex) {
            return null;
        }
    }, [parsedData])

    
    if (!video) return null;
    if (!coordinates) return null;

    return (
        <div className={styles.wrapper}>
            <span className={styles.icon}>
                <GeoIcon /> 
            </span>
            {' '}
            {coordinates.latitude}, {coordinates.longitude}
        </div>  
    )
}

export default Geoposition;
