import {DatePicker, DatePickerProps} from 'antd';
import React from 'react';
import classnames from 'classnames';
import styles from './Datepicker.module.scss';

class DatepickerCustom extends React.Component<DatePickerProps> {
    constructor(props: DatePickerProps) {
        super(props)
    }

    render() {
        return (
            <DatePicker 
                {...this.props}
                className={classnames(styles.datepicker, this.props.className)}
            />
        )
    }
}

export default DatepickerCustom;