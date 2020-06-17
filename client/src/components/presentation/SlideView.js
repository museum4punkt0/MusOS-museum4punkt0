/**
 * SlideView React component
 * 
 * @author    Jens Gruschel
 * @copyright © 2019 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


import React from 'react';
import ReactMarkdown from 'react-markdown';
import {getMediaType} from "../../utils";


class SlideView extends React.Component {

    render() {

        const backgroundMediaUrl = this.props.backgroundMediaUrl;
        const hasBackgroundVideo = backgroundMediaUrl && getMediaType(backgroundMediaUrl) === "video";
        const hasBackgroundImage = backgroundMediaUrl && !hasBackgroundVideo;

        const backgroundStyle = {
            position: "absolute",
            top: 0,
            bottom: 0,
            left: 0,
            right: 0,
            backgroundImage: hasBackgroundImage && "url(" + backgroundMediaUrl + ")",
            backgroundPosition: "center",
            backgroundRepeat: "no-repeat",
            backgroundSize: "cover"
        };

        const backgroundVideoElement = hasBackgroundVideo &&
            <video key={backgroundMediaUrl} autoPlay loop id="bgVideo" style={{
                position: "absolute",
                left: "50%",
                top: "50%",
                transform: "translate(-50%, -50%)",
                width: "auto",
                height: "auto",
                minWidth: "100%",
                minHeight: "100%"
            }}>
                <source src={backgroundMediaUrl} type="video/mp4"/>
            </video>;

        // the outermost div takes care of the layout,
        // the next div does nothing, but can be referenced by customized CSS,
        // the inner div controls the background (as defined for the specific slide),
        // the title and markdown widget within both have another class name for customized CSS

        return (
            <div style={{position: "absolute", top: 0, bottom: 0, left: 0, right: 0}}>
                <style>
                    {this.props.stylesheet}
                </style>

                <div className="slidescreen" style={{position: "absolute", top: 0, bottom: 0, left: 0, right: 0}}>
                    <div className="slidelayout" style={backgroundStyle}>
                        {backgroundVideoElement}
                        <div className="slideimages">
                        {
                            this.props.images ? this.props.images.map(image => (
                                <div key={image} className="slideimage"><img src={image} alt="" /></div>
                            )) : undefined
                        }
                        </div>
                        <div className="slidecontent">
                            <h1 className="slidetitle">{this.props.title}</h1>
                            <ReactMarkdown className="slide" source={this.props.text} />
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

export default SlideView;