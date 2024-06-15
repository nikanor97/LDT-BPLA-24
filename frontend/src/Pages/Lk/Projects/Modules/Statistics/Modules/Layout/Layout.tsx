import * as React from 'react';
import {Row, Col} from 'antd';
import styles from './Layout.module.scss'


type iLayout = {
    items: JSX.Element[];
}

const Layout = (props: iLayout) => {
    return (
        <div className={styles.wrapper}>
            <Row gutter={[16, 0]}>
                {
                    props.items.map((item, index) => {
                        return (
                            <Col 
                                key={index}
                                span={8}>
                                {item}
                            </Col>
                        )
                    })
                }
            </Row>
        </div>
    )
}

export default Layout;