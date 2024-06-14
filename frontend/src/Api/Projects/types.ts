import {User, Project, Viewer, Video, Photo} from '@root/Types';
import {RcFile} from 'antd/es/upload';


type FloorStat = {
    floor: number;
    value: number;
}
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
        content_id: Viewer.Id;
    }
    type oGetContentInfo = Video.Item
    type iGetContentFrames = {
        content_id: Video.Id;
    }
    type oGetContentFrames = Video.Frames.MarkupedItem[];

    type iGetProjectContent = {
        project_id: Project.Id;
    }
    type oGetProjectContent = Array<Video.Item | Photo.Item>;

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
        content_id: Video.Id;
        new_status: Video.Status;
    }

    type oChangeContentStatus = Video.Item;

    type iGetProjectFullStats = {
        project_id: Project.Id;
    }
    type oGetProjectFullStats = {
        avg_floor: {
            doors_pct: number,
            trash_bool: boolean,
            switch_total: number,
            window_decor_pct: number,
            radiator_pct: number,
            kitchen_total: number,
            toilet_pct: number,
            bathtub_pct: number,
            sink_pct: number,
            floor: {
                no_decor: number,
                rough_decor: number,
                finishing_decor: number
            },
            wall: {
                no_decor: number,
                rough_decor: number,
                finishing_decor: number
            },
            ceiling: {
                no_decor: number,
                rough_decor: number,
                finishing_decor: number
            },
            mop_floor: {
                no_decor: number,
                rough_decor: number,
                finishing_decor: number
            },
            mop_wall: {
                no_decor: number,
                rough_decor: number,
                finishing_decor: number
            },
            mop_ceiling: {
                no_decor: number,
                rough_decor: number,
                finishing_decor: number
            }
        }
        for_floor: {
            finishing: FloorStat[];
            no_decoration: FloorStat[]
        }
        
    }
}