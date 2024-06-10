export type Filters = {
    mode: 'home' | 'floor'
    detalisation: 'mop' | 'not_mop'
}

export type Item = {
    total_apartments: number;
    total_videos: number;
    apartments_approved: number;
}