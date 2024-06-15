import React, {useState} from 'react';
import {Drawer, Button, Form, Upload, message} from 'antd';
import { useDispatch, useSelector } from 'react-redux';
import {PageState} from '../../../../../../Redux/types';
import {PageActions} from '../../../../../../Redux/Store';
import {RcFile} from "antd/es/upload";
import {iForm} from './types';

const {Dragger} = Upload;


const UploadDrawer = () => {
    const [files, setFiles] = useState<RcFile[]>([]);
    const dispatch = useDispatch();
    const visible = useSelector((state: PageState) => state.Pages.LkProject.uploadDrawer.visible);
    const uploadFetching = useSelector((state: PageState) => state.Pages.LkProject.uploadContent.fetching);
    const project = useSelector((state: PageState)  => state.Pages.LkProject.getProject.data);
    const [form] = Form.useForm<iForm>();

    if (!project) return null;

    return (
        <Drawer 
            width={520}
            title={`Загрузка контента`}
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
                onFinish={() => {
                    dispatch(PageActions.uploadContent({
                        onSuccess: () => {
                            dispatch(PageActions.closeUploadDrawer());
                            setFiles([]);
                        },
                        onError: () => {
                            message.error('Ошибка при загрузке видео')
                        },
                        params: {
                            project_id: project.id,
                            document: files,
                        }
                    }))
                }}
                form={form}>
                <Dragger
                    name="documents"
                    beforeUpload={(file, fileList) => {
                        setFiles(fileList);
                        return false;
                    }}
                    fileList={files}
                    accept='.mp4,.png,.jpg,.jpeg'
                    onRemove={(file) => {
                        setFiles(files.filter((item) => item.uid !== file.uid));
                    }}
                    multiple={true}>
                    <div>
                        Нажмите или перенесите в эту область файлы для загрузки
                    </div>
                </Dragger>
            </Form>
        </Drawer>
    )
}

export default UploadDrawer;