import {User, Apartment} from '../';

export type Status = 
    'created' | 
    'extracted' | 
    'approved' | 
    'declined';


export type Id = string;
export type Item = {
    "id": string;
    "created_at": string;
    "updated_at": string;
    "name": string;
    "description": string;
    "owner_id": User.Id;
    "status": Status
    "apartment_id": Apartment.Id,
    "length_sec": number,
    "n_frames": number,
    "height": number,
    "width": number,
    "source_url": string;
	"type": "video" | "photo";
	"detected_count": number
}