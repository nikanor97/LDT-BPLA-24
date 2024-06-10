import React, {useState} from 'react';
import {Drawer, Button, Form, Upload, message} from 'antd';
import { useDispatch, useSelector } from 'react-redux';
import {PageState} from '../../../../Redux/types';
import {PageActions} from '../../../../Redux/Store';
import { required } from '@root/Utils/Form/Rules';
import {Input} from '@root/Components/Controls';
import {RcFile} from "antd/es/upload";
import {iForm} from './types';
import { getApartName } from '@root/Utils/Apartment/getApartName';

const {Dragger} = Upload;


const UploadDrawer = () => {
    const [files, setFiles] = useState<RcFile[]>([]);
    const dispatch = useDispatch();
    const visible = useSelector((state: PageState) => state.Pages.LkApartment.uploadDrawer.visible);
    const apartment = useSelector((state: PageState) => state.Pages.LkApartment.apartment.data);
    const uploadFetching = useSelector((state: PageState) => state.Pages.LkApartment.uploadVideo.fetching);
    const [form] = Form.useForm<iForm>();

    if (!apartment) return null;

    return (
        <Drawer 
            width={520}
            title={`Загрузка видео. ${getApartName(apartment.number)}}`}
            onClose={() => {
                dispatch(PageActions.closeUploadDrawer());
            }}
            footer={
                <Button 
                    disabled={files.length === 0}
                    onClick={() => {
                        form.submit();
                    }}
                    loading={uploadFetching}
                    type="primary">
                    Загрузить
                </Button>
            }
            open={visible}>
            <Form 
                layout="vertical"
                onFinish={(values) => {
                    dispatch(PageActions.uploadVideo({
                        onSuccess: () => {
                            dispatch(PageActions.getApartment({apartId: apartment.id}))
                            dispatch(PageActions.getVideos({apartment_id: apartment.id}))
                            dispatch(PageActions.closeUploadDrawer());
                        },
                        onError: () => {
                            message.error('Ошибка при загрузке видео')
                        },
                        params: {
                            ...values,
                            project_id: apartment.id,
                            document: files,
                        }
                    }))
                }}
                form={form}>
                <Form.Item 
                    label="Имя видео"
                    rules={[required]}
                    name="name">
                    <Input placeholder="Введите имя для отображения" />
                </Form.Item>
                <Form.Item 
                    label="Описание"
                    rules={[required]}
                    name="description">
                    <Input placeholder="Введите описание для отображения" />
                </Form.Item>
                <Dragger
                    name="documents"
                    beforeUpload={(file, fileList) => {
                        setFiles(fileList);
                        return false;
                    }}
                    onRemove={() => {
                        setFiles([]);
                    }}
                    multiple={false}>
                    <div>
                        Нажмите или перенесите в эту область файлы для загрузки
                    </div>
                </Dragger>
            </Form>
        </Drawer>
    )
}

export default UploadDrawer;