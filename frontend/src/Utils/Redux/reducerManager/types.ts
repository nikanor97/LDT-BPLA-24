export declare namespace iState {
    type Value = {
        action: null | 'add' | 'remove';
        date: null | string;
        name: null | string;
    }
}

export declare namespace iActions {
    type changePage = {
        name: string;
        action: 'add' | 'remove'
    }
}