import {useEffect} from 'react';
import GridContainer from '@root/Components/GridContainer/GridContainer';
import Header from './Modules/Header/Header';
import styles from './Projects.module.scss';
import PageStateContainer from '@root/Containers/PageState/PageState';
import {Slice} from './Redux/Store';
import { useDispatch } from 'react-redux';
import Sagas from './Saga/ProjectsSaga';
import {PageActions} from './Redux/Store';
import Table from './Modules/Table/Table';
import CreateProject from './Modules/CreateProject/CreateProject';
import Statistics from './Modules/Statistics/Statistics';

const Projects = () => {
    const dispatch = useDispatch();
    useEffect(() => {
        dispatch(PageActions.getProjects())
    }, [])

    return (
        <PageStateContainer params={[Slice, [Sagas]]}>
            <div className={styles.wrapper}>
                <GridContainer className={styles.container}>
                    <>
                        <Header />
                        <Statistics />
                        <Table />
                        <CreateProject />
                    </>
                </GridContainer>
            </div>
        </PageStateContainer>
    )
}


export default Projects;