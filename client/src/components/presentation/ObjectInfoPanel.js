/**
 * ObjectInfoPanel React component
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
import React from 'react';
import {connect} from 'react-redux';

// 3rd party
import { useDrop } from 'react-dnd'

// application
import {DRAGGABLE_MENU_OBJECT_TYPE} from "./DraggableMenuObject";
import {patchServerUrl} from "../../config";
import {selectFieldValue, selectFieldName} from "../../redux/types/selectors";
import {selectTranslation} from "../../redux/configuration/selectors";
import {findTaggedImage} from "../../utils";


class ObjectInfoPanel extends React.Component {

    render() {

        // the outermost div takes care of the layout,
        // the next div does nothing, but can be referenced by customized CSS,
        // the inner div controls the background (as defined for the specific slide),
        // the title and markdown widget within both have another class name for customized CSS

        return <div style={{position: "absolute", top: 0, bottom: 0, left: 0, right: 0}}>
            <style>
                {this.props.stylesheet}
            </style>

            <div className="objectinfopanel" style={{position: "absolute", top: 0, bottom: 0, left: 0, right: 0}}>
                <div className="objectinfolayout">
                    <h1 className="objectinfotitle">{this.props.title}</h1>
                    <div className="objectinfocontainer">
                    {
                        this.props.subjects.map((subject, index) => <ObjectInfo
                            key={(subject && (subject.id + "/" + index)) || index}
                            subject={subject}
                            index={index}
                            fields={this.props.fields[index]}
                            referencedObjects={this.props.referencedObjects[index]}
                            imagetags={this.props.imagetags}
                        />)
                    }
                    </div>
                </div>
            </div>
        </div>;
    }

}


function ObjectInfo(props) {

    const { subject, index, fields, referencedObjects, imagetags } = props;

    const taggedImage = subject && findTaggedImage(subject, referencedObjects, imagetags);
    const taggedImageUrl = patchServerUrl((taggedImage && taggedImage.fields && taggedImage.fields.url) || (subject && subject.imageurl));

    const [{ isOver, canDrop }, drop] = useDrop({
        accept: DRAGGABLE_MENU_OBJECT_TYPE,
        canDrop: () => true,
		drop: (item, monitor) => ({
            item: item,
            index: index
        }),
		collect: monitor => ({
            isOver: !!monitor.isOver(),
            canDrop: !!monitor.canDrop()
		}),
	})

    return <div
        ref={drop}
        className={"objectinfo" + (!subject ? " missing" : "") + (canDrop ? " dragging" : "") + (isOver ? " dropping" : "")}
    >
        <div className="objectinfoimage">
            {subject && subject.imageurl && <img src={taggedImageUrl}/>}
        </div>
        <ul>
            {
                fields.map(field => <li key={field.id} className={"field-" + field.id}>
                    <label>{field.name}</label>
                    <p>{field.value}</p>
                </li>)
            }
        </ul>
    </div>;
}


const mapStateToProps = (state, props) => {

    const quantity = props.quantity || 1;
    const fieldIds = props.fieldIds || [];

    const missing = Math.max(quantity - state.cbox.context.subjects.length, 0);
    const subjects = [...state.cbox.context.subjects.slice(0, quantity), ...Array(missing).fill(null)];
    const referencedObjects = [...state.cbox.context.referencedObjects.slice(0, quantity), ...Array(missing).fill(null)];
    const fields = subjects.map(
        subject => fieldIds.map(
            fieldId => ({
                id: fieldId,
                name: (subject && selectFieldName(state.types, subject.type, fieldId)) || fieldId,
                value: (subject && selectTranslation(state.configuration, selectFieldValue(state.types, {}, subject, fieldId, true))) || ""
            })
        )
    );

    return {
        subjects: subjects,
        referencedObjects: referencedObjects,
        fields: fields,
    };
};

export default connect(mapStateToProps)(ObjectInfoPanel);