/**
 * DraggableMenuObject React component
 * 
 * @author    Jens Gruschel
 * @copyright © 2020 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


// React
import React, { useContext } from 'react';

// 3rd party
import { useDrag } from 'react-dnd'
import { Preview } from 'react-dnd-multi-backend';

export const DRAGGABLE_MENU_OBJECT_TYPE = 'DRAGGABLE_MENU_OBJECT';


/**
 * DraggableMenuObject
 *
 * @author Jens Gruschel
 */
function DraggableMenuObject(props) {

    // own props
    const { id, imageUrl, labelText, onDrop } = props;

    const [{ isDragging }, drag] = useDrag({
        item: {
            type: DRAGGABLE_MENU_OBJECT_TYPE,
            id: id,
            props: {
                imageUrl: imageUrl,
                labelText: labelText
            }
        },
        end: (item, monitor) => {
            if (monitor.didDrop()) {
                const result = monitor.getDropResult();
                onDrop(result && result.index)
            }
        },
        collect: monitor => ({
            isDragging: !!monitor.isDragging(),
        })
    });

    return <div
        ref={drag}
        style={{
            opacity: isDragging ? 0 : 1,
            cursor: 'move'
        }}
    >
        {imageUrl && <img src={imageUrl} alt={labelText} />}
        <label>{labelText}</label>
    </div>;
}


export const DraggableMenuObjectPreview = (props) => {
    const { className } = props;
    const { style, item } = useContext(Preview.Context);
    const { imageUrl, labelText } = item.props;
    return <div
        className={className}
        style={{
            ...style,
            opacity: 1
        }}
    >
        {imageUrl && <img src={imageUrl} alt={labelText} />}
        <label>{labelText}</label>
    </div>;
};


export default DraggableMenuObject;