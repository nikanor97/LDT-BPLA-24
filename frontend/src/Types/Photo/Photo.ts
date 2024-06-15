import {User, Project} from '..';

export type Status = 
    'created' | 
    'extracted' | 
    'approved' | 
    'declined';


export type Id = string;
export type Item = {
    "content_id": string;
    "created_at": string;
    "updated_at": string;
    "owner_id": User.Id;
    "status": Status
    "project_id": Project.Id,
    "height": number,
    "width": number,
    "source_url": string;
	"content_type": "video" | "photo";
	"detected_count": number,
}

