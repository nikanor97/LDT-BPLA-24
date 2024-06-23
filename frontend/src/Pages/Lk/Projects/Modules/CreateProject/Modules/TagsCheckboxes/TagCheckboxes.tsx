import React, {useMemo} from 'react';
import {Alert, InputNumber, Space} from 'antd';
import {useSelector} from 'react-redux';
import {PageState} from '../../../../Redux/types';
import {Checkbox} from '@root/Components/Controls';
import styles from './TagCheckboxes.module.scss';
import {groupBy} from 'lodash';
import { Tag } from '../../CreateProject';
import Hint from '@root/Components/Hint/Hint';

type iTagCheckboxes = {
    value?: string[] | undefined;
    onChange?: (values: string[]) => any;
    setTags?: React.Dispatch<React.SetStateAction<Tag[]>>;
    className?: string;
    tagsArray: Tag[];
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
                                            const tagsArr = tags.map((item) => {
                                                return ({
                                                    tag_id: item.id,
                                                    conf: item.default_confidence
                                                })
                                            });
                                            tagsArr.forEach((tag) => {
                                                const find = props.tagsArray.find(
                                                    item => item.tag_id === tag.tag_id
                                                );
                                                if (find) {
                                                    return null;
                                                } else {
                                                    props.setTags && props.setTags((previous) => [...previous, tag]);
                                                }
                                            })

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
                                                <div key={tag.id} className={styles.checkboxZone}>
                                                    <Checkbox 
                                                        checked={value.includes(tag.id)}
                                                        onChange={(event) => {
                                                            const checked = event.target.checked;
                                                            if (checked) {
                                                                if (props.onChange) {
                                                                    props.onChange([...value, tag.id])
                                                                }
                                                                props.setTags && props.setTags([...props.tagsArray, {
                                                                    tag_id: tag.id,
                                                                    conf: 0
                                                                }]);
                                                            } else {
                                                                if (props.onChange) {
                                                                    const filtered = value.filter((item) => item !== tag.id);
                                                                    const filteredTags = props.tagsArray.filter((item) => item.tag_id !== tag.id);
                                                                    props.setTags && props.setTags(filteredTags);
                                                                    props.onChange(filtered);
                                                                }
                                                            }
                                                        }}>
                                                        {tag.tagname}
                                                    </Checkbox>
                                                    {value.includes(tag.id) && (
                                                        <>
                                                            <span className={styles.confText}>Конфиденс: <Hint title={"Введите число от 0 до 1"} /></span>
                                                            <InputNumber
                                                                defaultValue={tag.default_confidence || 0}
                                                                min={0}
                                                                max={1}
                                                                step={0.05}
                                                                onChange={(value) => {
                                                                    const myNextList = [...props.tagsArray];
                                                                    const changeTag = myNextList.find(
                                                                        item => item.tag_id === tag.id
                                                                    );
                                                                    if (changeTag) {
                                                                        changeTag.conf = value;
                                                                        props.setTags && props.setTags(myNextList);
                                                                    } else {
                                                                        props.setTags && props.setTags([...myNextList, {
                                                                            tag_id: tag.id,
                                                                            conf: value
                                                                        }]);
                                                                    }
                                                                }}/>
                                                        </>
                                                    )}

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