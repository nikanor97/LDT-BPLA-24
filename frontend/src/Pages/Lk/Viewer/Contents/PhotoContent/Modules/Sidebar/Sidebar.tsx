import * as React from 'react';
import styles from './Sidebar.module.scss';
import Labels from './Modules/Labels/Labels';
import { usePhoto } from '../../Hooks/usePhoto';
import { useDispatch, useSelector } from 'react-redux';
import {PageActions} from '../../../../Redux/Store';
import {PageState} from '../../../../Redux/types';
import { Button } from 'antd';
import Markup from './Modules/Markup/Markup';
import InfoIcon from '@root/Components/Hint/Icons/InfoIcon';

const Sidebar = () => {
    const photo = usePhoto();
    const dispatch = useDispatch();
    const viewMode = useSelector((state: PageState) => state.Pages.LkViewer.viewMode);

    const getContent = ()  =>  {
        if (viewMode  ===  "markup")  { 
            return (
                <>
                    <div className={styles.title}>
                        Разметить данные
                    </div>
                    <div className={styles.desc}>
                        <div className={styles.content}>
                            <InfoIcon />
                            <div className={styles.text}>
                                <span>
                                Для разметки данных необходимо:
                                </span>
                                <ol>
                                    <li>
                                    Выбрать класс данных;
                                    </li>
                                    <li>
                                    Зажать <strong>Shift</strong> и выделить необходимую область на изображении/видео;
                                    </li>
                                    <li>
                                    При разметке видео, поставьте его на паузу.
                                    </li>
                                </ol>
                            </div>
                        </div>
                    </div>
                    <span className={styles.markupsTitle}>Класс данных</span>
                    <Markup />
                </>
            )
        }
        return (
            <>
                <div className={styles.title}>
                    Обнаруженные объекты
                    {
                        photo && (
                            <Button
                                onClick={() => {
                                    dispatch(PageActions.downloadResult({
                                        content_id: photo.content_id
                                    }));
                                }}>
                            Скачать результаты
                            </Button>
                        )
                    }
                </div>
                <Labels />
            </>
        )
    }

    return (
        <div className={styles.wrapper}>
            {getContent()}
        </div>
    )
}


export default Sidebar;