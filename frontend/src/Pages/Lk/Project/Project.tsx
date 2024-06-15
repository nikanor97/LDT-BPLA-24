import React, {useEffect} from 'react';
import {useParams} from 'react-router-dom';
import {Params} from './types';
import {useDispatch} from 'react-redux';
import GridContainer from '@root/Components/GridContainer/GridContainer';
import {PageActions} from './Redux/Store';
import PageStateContainer from '@root/Containers/PageState/PageState';
import ContentController from './Controllers/ContentController';
import {Slice} from './Redux/Store';
import Sagas from './Saga/ProjectsSaga';
import styles from './Project.module.scss';

const Project = () => {
    const params = useParams<Params>();
    const dispatch = useDispatch();
    
    useEffect(() => {
        dispatch(PageActions.getProject(params.projectId))
        dispatch(PageActions.getProjectContent({project_id: params.projectId}))
    }, []);

    return (
        <PageStateContainer params={[Slice, [Sagas]]}>
            <>
                <GridContainer className={styles.container}>
                    <ContentController />
                </GridContainer>
            </>
        </PageStateContainer>
    )
}


export default Project;