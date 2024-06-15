import {Input, InputProps, InputRef} from 'antd';
import React from 'react';
import classnames from 'classnames';
import styles from './input.module.scss';
import {PasswordProps} from 'antd/lib/input';

const CustomPassword = React.forwardRef<InputRef, PasswordProps>((props, ref) => {
    return React.createElement(
        Input.Password, 
        {
            ...props,
            ref,
            className: classnames(
                styles.password,
                props.className
            )
        }
    )
})

class CustomInput extends React.Component<InputProps> {
    constructor(props: InputProps) {
        super(props)
    }

    static TextArea = Input.TextArea;
    static Password = CustomPassword;
    render() {
        return (
            <Input 
                {...this.props}
                className={classnames(styles.input, this.props.className)}
            />
        )
    }
}

export default CustomInput;