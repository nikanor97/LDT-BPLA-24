import React, {useEffect, useState} from 'react';
import {Drawer, Form, Button, message} from 'antd';
import {useDispatch, useSelector} from 'react-redux';
import {Input} from '@root/Components/Controls';
import {PageState} from '../../Redux/types';
import {iForm} from './types';
import {PageActions} from '../../Redux/Store';
import {required} from '@root/Utils/Form/Rules';
import TagCheckboxes from './Modules/TagsCheckboxes/TagCheckboxes'
import styles from './CreateProject.module.scss';
import Hint from '@root/Components/Hint/Hint';

export type Tag = {
    tag_id: string,
    conf: 0 | 1 | null
}

const CreateProject = () => {
    const visible = useSelector((state:PageState) => state.Pages.LkProjects.createDrawer.visible);
    const user = useSelector((state: PageState) => state.User.Info.data);
    const state = useSelector((state:PageState) => state.Pages.LkProjects.create);
    const [tags, setTags] = useState<Tag[]>([])
    const [form] = Form.useForm<iForm>();
    const dispatch = useDispatch();

    useEffect(() => {
        dispatch(PageActions.getTags());
    }, []);

    return (
        <Drawer 
            title="Создать проект"
            width={560}
            onClose={() => {
                dispatch(PageActions.closeCreateProject());
            }}
            footer={
                <Button 
                    onClick={() => form.submit()}
                    loading={state.fetching}
                    type="primary">
                    Создать
                </Button>
            }
            open={visible}>
            <div>
                <Form 
                    onFinish={(values) => {
                        if (!user) return;
                        const data = {
                            name: values.name,
                            tags: tags,
                            msg_receiver: values.msg_receiver,
                        }
                        dispatch(PageActions.createProject({
                            params: data,
                            onSuccess: () => {
                                dispatch(PageActions.closeCreateProject());
                                dispatch(PageActions.getProjects());
                                message.success('Проект успешно создан');
                            },
                            onError: () => {
                                message.error('Ошибка при создании проекта');
                            }
                        }))
                    }}
                    layout="vertical"
                    form={form}>
                    <Form.Item
                        name="name"
                        rules={[required]}
                        label="Название проекта">
                        <Input  placeholder="Введите название проекта" />
                    </Form.Item>
                    <Form.Item 
                        name="tags_ids"
                        rules={[required]}
                        label="Объекты детекции">
                        <TagCheckboxes className={styles.checkboxes} setTags={setTags} tagsArray={tags}/>
                    </Form.Item>
                    <Form.Item 
                        name="msg_receiver"
                        label={
                            <div className={styles.label}>
                                Контакт ответственного
                                <Hint title={() => "Контакт ответственного лица в Telegram, для оповещения о детекции объектов"}/>
                            </div>}>
                        <Input  placeholder="Введите ник в телеграме @name" />
                    </Form.Item>
                </Form>
            </div>
        </Drawer>
    )
}


export default CreateProject;