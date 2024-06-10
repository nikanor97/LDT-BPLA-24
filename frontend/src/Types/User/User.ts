

export type Id = string;

export type Info = {
    "id": Id;
    "created_at": string;
    "updated_at": string;
    "name": string;
    "email": string;
}

export type Token = {
    access_token: string,
    refresh_token: string,
    token_type: string,
    access_expires_at: number;
    refresh_expires_at: number
}

export type SystemRolesValues = Record<SystemRole, boolean>;
export type SystemRole = 
    "unauth" |
    "requested" |
    "auth";
