import React, {useEffect, useMemo} from 'react';
import {User} from '@root/Types';
import {useUserRoles} from '@root/Hooks/User/useUserRoles';

type iCheckRole = {
    roles: User.SystemRole[];
    children: JSX.Element;
    error?: JSX.Element;
    onError?: (roles: User.SystemRolesValues) => any; 
}

const CheckRole = (props: iCheckRole) => {
    const userRoles = useUserRoles();
    const result = useMemo(() => {
        const values = props.roles.map((role) => userRoles[role])
        return values.some(Boolean);
    }, [userRoles, props.roles]);


    useEffect(() => {
        if (!result) {
            props.onError && props.onError(userRoles);
        }
    }, [result])
    
    if (!result) {
        if (props.error) {
            return props.error;
        } else {
            return null;
        }
    } else {
        return props.children;
    }
}


export default CheckRole;