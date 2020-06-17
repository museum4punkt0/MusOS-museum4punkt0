/**
 * ContentView React component
 * 
 * @author    Jens Gruschel, Maurizio Tidei
 * @copyright © 2019 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


// React
import React from 'react';
import PropTypes from 'prop-types';

// Material-UI
import {withStyles} from "@material-ui/core";

// application
import MediaPanel from "../base/MediaPanel";
import SlideView from "./SlideView";
import ObjectInfoPanel from "./ObjectInfoPanel";


/**
 * ContentView
 *
 * @author Jens Gruschel, Maurizio Tidei
 */
class ContentView extends React.Component {

    render() {

        const {content, screenIndex} = this.props;

        if (content && content.fields) {

            switch (content.type) {

                case "mediaitem": {

                    return <MediaPanel
                        // style={{position: "absolute", left: 0, right: 0, top: 0, bottom: 0}}
                        url={content.fields.url}
                        restart={this.props.restart}
                        autoplay={true}
                        showControls={false}
                        full={true}
                        loop={this.props.loop}
                        paused={this.props.paused}
                        volume={this.props.volume}
                    />;
                }
                case "textslide": {

                    // find style sheet
                    const styleSheets = this.findReferencedObjects(content.fields.style);
                    const styleSheetDefinition = styleSheets && styleSheets.length > 0 && styleSheets[0].fields ? styleSheets[0].fields.definition : null;

                    // find background image URL (if any)
                    const backgrounds = this.findReferencedObjects(content.fields.backgroundImage);
                    const backgroundMediaUrl = backgrounds && backgrounds.length > 0 && backgrounds[0].fields ? backgrounds[0].fields.url : null;

                    // find images
                    const images = this.findReferencedObjects(content.fields.images);
                    const imageUrls = images.map(item => item && item.fields ? item.fields.url : null);

                    return <SlideView
                        title={content.fields.title}
                        text={content.fields.text}
                        images={imageUrls}
                        stylesheet={styleSheetDefinition}
                        backgroundColor={content.fields.backgroundColor}
                        backgroundMediaUrl={backgroundMediaUrl}
                    />;
                }
                case "objectinfopanel": {

                    // find style sheet
                    const styleSheets = this.findReferencedObjects(content.fields.style);
                    const styleSheetDefinition = styleSheets && styleSheets.length > 0 && styleSheets[0].fields ? styleSheets[0].fields.definition : null;

                    return <ObjectInfoPanel
                        quantity={content.fields.quantity}
                        title={content.fields.title}
                        fieldIds={content.fields.fieldIds}
                        stylesheet={styleSheetDefinition}
                        imagetags={content.fields.imagetags}
                    />;

                }
                case "htmlcontent": {

                    return <iframe
                        key={"external-html-" + this.props.restart}
                        title="external"
                        id="external"
                        className={this.props.classes.iframeElement}
                        src={content.fields.link}
                        style={{backgroundColor: content.fields.backgroundColor}}
                        scrolling="no"
                    />;
                }
                default: {

                    return <div>unknown content type</div>;
                }
            }
        }

        else {

            return <div />;
        }
    }

    findReferencedObjects(field) {
        if (field && this.props.referencedObjects) {
            if(field instanceof Array) {
                return field.map(id => this.props.referencedObjects[id]);
            } else {
                return this.props.referencedObjects[field];
            }
        }
        else {
            return [];
        }
    }
}

ContentView.propTypes = {
    screenIndex: PropTypes.number,
    content: PropTypes.object,
    referencedObjects: PropTypes.object,
    loop: PropTypes.bool,
    paused: PropTypes.bool,
    volume: PropTypes.number,
    restart: PropTypes.any,
    navigationIndex: PropTypes.array,
};

const styles = theme => ({
    iframeElement: {
        width: "100%",
        height: "100%",
        borderStyle: "none"
    }
});

export default withStyles(styles)(ContentView);