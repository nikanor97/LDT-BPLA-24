import * as React from 'react';
import {Apartment} from '@root/Types';
import Node from '../Node/Node';
import Leaf from '../Leaf/Leaf';


type iController = {
    item: Apartment.Scores.LeafItem | Apartment.Scores.NodeItem;
    itemKey: string;
}

const {Guards} = Apartment;

const Controller = (props: iController) => {
    const {item} = props;
    if (Guards.Scores.isNode(item)) {
        return (
            <Node 
                item={item}
                itemKey={props.itemKey}
            />
        )
    } else {
        return (
            <Leaf 
                item={item}
                key={props.itemKey}
            />
        )
    }
}


export default Controller;