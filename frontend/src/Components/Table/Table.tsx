import * as React from 'react';
import {TableProps, Table} from 'antd';
import styles from './Table.module.scss';
import classnames from 'classnames';


class CustomTable<T extends object = any> extends React.Component<TableProps<T>> {
    constructor(props: TableProps<T>) {
        super(props)
    }

    
    render() {
        
        return (
            <div className={styles.wrapper}>
                <Table 
                    {...this.props}
                    className={classnames(styles.table, this.props.className)}
                />
            </div>
        )
    }
}

export default CustomTable