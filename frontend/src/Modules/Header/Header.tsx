import React, {useMemo} from 'react';
import classnames from 'classnames';
import styles from './Header.module.scss';
import Logotype from '@root/Img/Logo.png';
import {Row, Col} from 'antd';
import UserAvatar from './Modules/UserAvatar/UserAvatar';
import GridContainer from '@root/Components/GridContainer/GridContainer';
import { Link } from 'react-router-dom';
import routes from '@root/routes';

type iHeader = {
    className?: string;
    Logo?: JSX.Element
    Content?: JSX.Element;
    User?:JSX.Element
}


const Header = (props: iHeader) => {
    const Logo = useMemo(() => {
        if (props.Logo) return props.Logo;
        return <Link to={routes.main}><img style={{width: "146px", height: "32px"}} src={Logotype} alt="logo"/></Link>
    }, [props.Logo])

    const Content = useMemo(() => {
        if (props.Content) return props.Content;
        return null
    }, [props.Content])

    const User = useMemo(() => {
        if (props.User) return props.User;
        return <UserAvatar />;
    }, [props.User])


    return (
        <header className={classnames(props.className, styles.wrapper)}>
            <GridContainer>
                <Row className={styles.row}>
                    <Col className={styles.logo}>
                        {Logo}
                    </Col>
                    <Col className={styles.content}>
                        {Content}
                    </Col>
                    <Col>
                        {User}
                    </Col>
                </Row>
            </GridContainer>
        </header>
    )
}


export default Header;