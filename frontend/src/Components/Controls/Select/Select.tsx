import {Select, SelectProps} from 'antd';
import React from 'react';
import classnames from 'classnames';
import styles from './Select.module.scss';

class CustomSelect extends React.Component<SelectProps> {
    constructor(props: SelectProps) {
        super(props)
    }

    static Option = Select.Option;

    render() {
        return (
            <Select 
                {...this.props}
                className={classnames(styles.select, this.props.className)}
            />
        )
    }
}

export default CustomSelect;