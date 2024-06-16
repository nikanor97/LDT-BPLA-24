import {User, Project, Viewer, Video, Photo} from '@root/Types';
import {RcFile} from 'antd/es/upload';


export declare namespace Api {
    type iGetProjects = User.Id;
    type oGetProjects = Project.Item[];

    type iGetProject = Project.Id;
    type oGetProject = Project.Info;

    type iDeleteProject = Project.Id;
    type oDeleteProject = Project.Info;

    type iCreateProject = {
        name: string;
        msg_receiver: string
        tags_ids: string[];
    }
    type oCreateProject = Project.Info;

    type iGetProjectVideos = {
        project_id: Project.Id;
    }
    type iUploadProjectVideo = {
        name: string;
        description: string;
        file: RcFile;
        project_id: Project.Id;
    }
    type oGetTags = Project.Tags.Item[];
    type iGetContentInfo = {
        content_id: Video.Item['content_id'] | Photo.Item['content_id'];
    }
    type oGetContentInfo = Video.Item
    type iGetContentFrames = {
        content_id: Video.Item['content_id'] | Photo.Item['content_id'];
    }
    type oGetContentFrames = Video.Frames.MarkupedItem[];

    type iGetProjectContent = {
        project_id: Project.Id;
    }
    type oGetProjectContent = Array<Video.Item | Photo.Item>;
    type iGetContentIds = {
        project_id: Project.Id;
    }
    type oGetContentIds = Array<Video.Item['content_id'] | Photo.Item['content_id']>;

    type iGetLabels = {
        project_id: string;
    }
    type oGetLabels = Project.Label.Item[];

    type iUploadContent = {
        project_id: Project.Id;
        document: RcFile[];
    }

    type oGetProjectsStats = Project.Statistics.Item;
    type oUploadContent = any; //TODO Поменять
    type oGetMyProjects = Project.ItemFull[];
    type iGetProjectStats = {
        project_id: Project.Id;
    }

    type iChangeContentStatus = {
        content_id: Video.Item['content_id'] | Photo.Item['content_id'];
        new_status: Video.Status;
    }

    type oChangeContentStatus = Video.Item;

    type iGetProjectFullStats = {
        project_id: Project.Id;
    }
    type iDownloadResult = {
        content_id: Video.Item['content_id'] | Photo.Item['content_id'];
    }
}