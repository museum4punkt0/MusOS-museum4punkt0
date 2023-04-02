/**
 * ObjectInfoPanel React component
 * 
 * @author    Jens Gruschel
 * @copyright © 2020 contexagon GmbH
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
import MediaPanel from "../base/MediaPanel";
import {openMediaOverlayForUrl} from "../../operations/view";
import {showAccordionItem} from "../../operations/cbox";
import MediaViewerOverlay from "../base/MediaViewerOverlay";
import ExpansionPanel from '@material-ui/core/ExpansionPanel';
import ExpansionPanelDetails from '@material-ui/core/ExpansionPanelDetails';
import ExpansionPanelSummary from '@material-ui/core/ExpansionPanelSummary';


class ObjectInfoPanel extends React.Component {

    handleAccordionChange = panel => (event, expanded) => {
        console.log("handleAccordionChange", panel, event, expanded);
        this.props.showAccordionItem(expanded ? panel : false);
    };

    render() {

        if(this.props.accordionSelected == null) {
            window.scrollTo(0,0);
        }

        console.log("ObjectInfoPanel.render()", this.props);

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
                            accordionSelected={this.props.accordionSelected}
                            index={index}
                            fields={this.props.fields[index]}
                            referencedObjects={this.props.referencedObjects[index]}
                            referencedMediaObjects={this.props.referencedMediaObjects}
                            imagetags={this.props.imagetags}
                            openMediaOverlayForUrl={this.props.openMediaOverlayForUrl}
                            handleAccordionSelection={this.handleAccordionChange}
                        />)
                    }
                    </div>
                </div>
            </div>
            <MediaViewerOverlay/>
        </div>;
    }
}



// This section is for the "Paternoster" part of MusOS - a extension made for the Fasnachtsmuseum Schloss Langenstein in the year 2021 as a special application.
// It is used for the big wall cabinets in the to be built museum building.
// Every media item and meta data entry with the respective tag will be included in this application. 

function ObjectInfo(props) {

    const { subject, index, fields, referencedObjects, referencedMediaObjects, imagetags, accordionSelected, handleAccordionSelection } = props;

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
	});

    return <div
        ref={drop}
        className={"objectinfo" + (!subject ? " missing" : "") + (canDrop ? " dragging" : "") + (isOver ? " dropping" : "")}
    >
        <div className="accimg">
            {subject && subject.imageurl && <img src={taggedImageUrl}/>}
        </div>
        <ul>
            {
                fields.map(field => {
                    const accordionKeyword = "#accordion#";
                    if(field.id !== "medialist") {
                        console.log("ObjectInfoPanel", field);
                        if(fields.map(field => field.id).includes(accordionKeyword) && field.id !== "menutitle") {
                            if(field.id !== accordionKeyword) {
                                return <ExpansionPanel expanded={accordionSelected === field.id} key={field.id} className={"accordion"} onChange={handleAccordionSelection(field.id)}>
                                    <ExpansionPanelSummary className={"accordionSummary"}>{field.name}</ExpansionPanelSummary>
                                    <ExpansionPanelDetails className={"accordionDetails"}>{field.value}</ExpansionPanelDetails>
                                </ExpansionPanel>
                            }
                        }
                        else {
                            return <li key={field.id} className={"field-" + field.id}>
                                <label>{field.name}</label>
                                <p>{field.value}</p>
                            </li>
                        }
                    } else {
                        return <ExpansionPanel expanded={accordionSelected === field.id} key={field.id} className={"accordion"} onChange={handleAccordionSelection(field.id)}>
                            <ExpansionPanelSummary className={"accordionSummary"}>Medien</ExpansionPanelSummary>
                            <ExpansionPanelDetails className={"accordionDetails"}>
                                {
                                     field.value.split(",").map(mediaId => {
                                        const id = mediaId.trim();
                                        const mediaItem = findMediaItem(id, referencedMediaObjects);
                                        if(mediaItem) {
                                            let mediaUrl = patchServerUrl(mediaItem.fields.url);
                                            return <MediaPanel url={mediaUrl} showControls={true} onClick={() => props.openMediaOverlayForUrl(mediaUrl, mediaItem.fields.title)}/>
                                        }
                                    })
                                }
                            </ExpansionPanelDetails>
                        </ExpansionPanel>
                    }
                })
            }
        </ul>
    </div>;
}


const findMediaItem = (id, referencedMediaObjects) => {

    for(var key of Object.keys(referencedMediaObjects)) {

        let mediaObject = referencedMediaObjects[key];
        if(id === mediaObject.id) {
            return mediaObject;
        }
    }
};


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
        referencedMediaObjects: props.referencedObjects,
        fields: fields,
        accordionSelected: state.cbox.accordionSelected
    };
};

export default connect(mapStateToProps, {openMediaOverlayForUrl, showAccordionItem})(ObjectInfoPanel);
