import {Checkbox, CheckboxProps} from 'antd';
import React from 'react';
import classnames from 'classnames';
import styles from './Checkbox.module.scss';

class CustomCheckbox extends React.Component<CheckboxProps> {
    constructor(props: CheckboxProps) {
        super(props)
    }

    static Group = Checkbox.Group;    
    render() {
        return (
            <Checkbox
                {...this.props}
                className={classnames(styles.checkbox, this.props.className)}
            />
        )
    }
}

export default CustomCheckbox;