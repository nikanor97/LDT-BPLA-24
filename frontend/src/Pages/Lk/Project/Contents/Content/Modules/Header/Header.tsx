import * as React from 'react';
import {useDispatch, useSelector} from 'react-redux';
import {PageState} from '../../../../Redux/types';
import {Link, useHistory} from 'react-router-dom';
import Routes from '@root/routes';
import {ArrowLeftOutlined} from '@ant-design/icons';
import styles from './Header.module.scss';
import StatusTag from '@root/Components/StatusTag/StatusTag';
import {getStatusText, getStatusType} from '@root/Utils/Project/getStatus'
import {declinationOfNumber} from '@root/Utils/Normalize/declinationOfNumber';
import {Button, Popconfirm, Space, message} from 'antd';
import {PageActions} from '../../../../Redux/Store';
import {UploadOutlined, DeleteOutlined} from '@ant-design/icons';
import routes from '@root/routes';


const Header = () => {
    const project = useSelector((state:PageState) => state.Pages.LkProject.getProject.data);
    const apartments = useSelector((state:PageState) => state.Pages.LkProject.apartments.data);
    const dispatch = useDispatch();
    const history  =  useHistory();

    if (!project) return null;

    return (
        <div className={styles.wrapper}>
            <Link 
                className={styles.link}
                to={Routes.lk.projects}>
                <ArrowLeftOutlined /> Назад
            </Link>
            <div className={styles.row}>
                <div className={styles.leftCol}>
                    <div className={styles.title}>
                        {project?.name} 
                    </div>
                    {
                        project && (
                            <StatusTag 
                                text={getStatusText(project.status)}
                                type={getStatusType(project.status)}
                            />
                        )
                    }
                    {
                        apartments && (
                            <div className={styles.meta}>
                                {declinationOfNumber({
                                    value: apartments.length,
                                    words: ['Объект', 'Объекта', 'Объектов']
                                })}
                            </div>
                        )
                    }
                </div>
                <div className={styles.rightCol}>
                    <Space size={18}>
                        <Button 
                            onClick={() => {
                                dispatch(PageActions.openUploadDrawer())
                            }}
                            icon={<UploadOutlined />}
                            type="primary">
                            Загрузить
                        </Button>
                        <Popconfirm
                            placement="bottom"
                            title="Уверены, что хотите удалить проект?"
                            onConfirm={() => {
                                dispatch(PageActions.deleteProject({
                                    onSuccess: ()  =>  history.push(routes.lk.projects),
                                    onError: ()  =>  message.error("Не удалось удалить проект"),
                                    project_id: project.id
                                }))
                            }}
                            okText="Да"
                            cancelText="Нет">
                            <Button
                                icon={<DeleteOutlined />}
                                type="default">
                                Удалить
                            </Button>
                        </Popconfirm>

                    </Space>
                </div>
            </div>
        </div>
    )
}


export default Header;