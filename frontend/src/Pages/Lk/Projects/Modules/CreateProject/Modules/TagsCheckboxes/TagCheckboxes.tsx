import React, {useMemo} from 'react';
import {Alert, Space} from 'antd';
import {useSelector} from 'react-redux';
import {PageState} from '../../../../Redux/types';
import {Checkbox} from '@root/Components/Controls';
import styles from './TagCheckboxes.module.scss';
import {groupBy} from 'lodash';

type iTagCheckboxes = {
    value?: string[] | undefined;
    onChange?: (values: string[]) => any;
    className?: string;
}

const TagCheckboxes = (props: iTagCheckboxes) => {
    const tags = useSelector((state: PageState) => state.Pages.LkProjects.tags);
    const value = useMemo(() => props.value || [], [props.value]);
    const groups = useMemo(() => {
        if (!tags.data) return null;
        return groupBy(tags.data, 'groupname');
    }, [])


    if (tags.error) return (
        <Alert 
            type="error"
            message="Ошибка при получении тегов"
        />
    )
    if (!groups) return null;

    return (
        <div className={props.className}>
            {   
                Object.entries(groups)
                    .map(([group, tags], index) => {
                        return (
                            <div
                                className={styles.item}
                                key={`${group}${index}`}>
                                <div className={styles.title}>
                                    {group} 
                                    {' '}
                                    <span 
                                        onClick={() => {
                                            if (props.onChange) {
                                                const tagsIds = tags.map((item) => item.id);
                                                const values = Array.from(new Set([...value, ...tagsIds]))
                                                props.onChange(values);
                                            }
                                        }}
                                        className={styles.checkAll}>
                                        Выбрать все
                                    </span>
                                </div>
                                <Space 
                                    size={12} 
                                    direction="vertical">
                                    {
                                        tags.map((tag) => {
                                            return (
                                                <div>
                                                    <Checkbox 
                                                        checked={value.includes(tag.id)}
                                                        onChange={(event) => {
                                                            const checked = event.target.checked;
                                                            if (checked) {
                                                                if (props.onChange) {
                                                                    props.onChange([...value, tag.id])
                                                                }
                                                            } else {
                                                                if (props.onChange) {
                                                                    const filtered = value.filter((item) => item !== tag.id);
                                                                    props.onChange(filtered);
                                                                }
                                                            }
                                                        }}>
                                                        {tag.tagname}
                                                    </Checkbox>
                                                </div>
                                            )
                                        })
                                    }
                                </Space>
                            </div>
                        )
                    })
                
            }
        </div>
    )
}

export default TagCheckboxes;