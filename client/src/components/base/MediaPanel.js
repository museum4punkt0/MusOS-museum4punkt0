/**
 * MediaPanel React component
 * 
 * @author    Maurizio Tidei, Jens Gruschel
 * @copyright © 2018 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


// React
import React from 'react';

// Material-UI
import {withStyles} from '@material-ui/core/styles';
import SaveIcon from "@material-ui/icons/SaveAlt";
import PropTypes from "prop-types";
import Button from "@material-ui/core/Button";

// application
import PdfPanel from "./PdfPanel";
import {getMediaType} from "../../utils";
import {patchServerUrl} from "../../config";


const ERROR_IMAGE_URL = "/placeholders/warning.svg";


/**
 * MediaPanel visualizes a media item according to its type
 *
 * @author Maurizio Tidei
 */
export class MediaPanel extends React.Component {

    constructor(props) {
        super(props);
        this.state = this.createUrlState();
    }

    attachSource(url) {
        if (this.playbackElement) {
            this.playbackElement.setAttribute('src', url);
            // this.playbackElement.load();
        }
    }

    detachSource() {
        // some browsers will not clean up videos properly,
        // so as a workaround at least remove the sources
        // (which are children of the video element)
        if (this.playbackElement) {
            this.playbackElement.removeAttribute('src');
            // this.playbackElement.load();
        }
    }

    setPlaybackElement(element) {
        if (this.playbackElement !== element) {
            // this.detachSource();
            this.playbackElement = element;
            // this.attachSource(patchServerUrl(this.props.url));
        }
    }

    createUrlState() {
        if (this.props.thumbnail) {
            return {
                imgUrl: this.props.thumbnail,
                fallbackUrl: this.props.url,
                errorUrl: ERROR_IMAGE_URL
            };
        }
        else {
            return {
                imgUrl: this.props.url,
                fallbackUrl: null,
                errorUrl: ERROR_IMAGE_URL
            }
        }
    }

    updateUrl() {
        this.setState(this.createUrlState());
    }

    updateVolume() {
        if (this.playbackElement) {
            let volume = parseFloat(this.props.volume);
            if (!isNaN(volume)) {
                if (volume < 0.0) volume = 0.0;
                else if (volume > 100.0) volume = 100.0;
                this.playbackElement.volume = volume * 0.01;
            }
        }
    }

    updatePausing() {
        if (this.playbackElement) {
            console.log("media panel pause", this.props.paused, Date.now());
            if (this.props.paused) this.playbackElement.pause();
            else this.playbackElement.play();
        }
    }

    restart() {
        if (this.playbackElement) {
            this.playbackElement.pause();
            this.playbackElement.currentTime = 0;
            this.playbackElement.load();
            this.updatePausing();
        }
    }

    componentDidMount() {
        // this.attachSource(this.props.url);
    }

    componentWillUnmount() {
        this.detachSource();
    }

    componentDidUpdate(prevProps) {
        if (this.props.url !== prevProps.url) {
            this.updateUrl();
        }
        if (this.props.volume !== prevProps.volume) {
            this.updateVolume();
        }
        if (this.props.restart !== prevProps.restart) {
            this.restart();
        }
        else if (this.props.paused !== prevProps.paused) {
            this.updatePausing();
        }
    }

    onImgError = () => {
        console.log("media image error", this.state);
        if (this.state.fallbackUrl) {
            this.setState({
                imgUrl: this.state.fallbackUrl,
                fallbackUrl: null,
            });
        }
        else if (this.state.errorUrl) {
            this.setState({
                imgUrl: this.state.errorUrl,
                errorUrl: null,
            });
        }
    }

    render() {

        const {classes, url} = this.props;

        if (!url) {
            return <div>NO URL</div>;
        }

        const mediaType = getMediaType(url);

        const conditionalAttributes = {}
        if(this.props.autoplay) {
            conditionalAttributes.autoPlay = !this.props.paused;
        }
        if(this.props.showControls) {
            conditionalAttributes.controls = true;
        }
        if(this.props.loop) {
            conditionalAttributes.loop = true;
        }
        if (this.props.volume != null && parseFloat(this.props.volume) === 0) {
            conditionalAttributes.muted = true;
        }

        // console.log("MediaPanel conditional props", conditionalAttributes);

        switch(mediaType) {

            case "video":

                return <video
                    ref={element => {this.setPlaybackElement(element)}}
                    src={patchServerUrl(url)} // better than using "attachSource"?
                    className={this.props.full ? classes.fullsize : classes.other}
                    {...conditionalAttributes}
                    onLoadStart={() => {this.updateVolume()}} // surprisingly volume cannot be set directly
                    onClick={(e) => {if(this.props.playOnClick === false) e.preventDefault();}} // preventDefault prevents video playback when clicking on video
                />;

            case "audio":

                return <audio
                    ref={element => {this.setPlaybackElement(element)}}
                    src={patchServerUrl(url)} // better than using "attachSource"?
                    className={classes.other}
                    {...conditionalAttributes}
                    onLoadStart={() => {this.updateVolume()}} // surprisingly volume cannot be set directly
                />;

            case "image":

                this.setPlaybackElement(null);
                return <img
                    className={this.props.full ? classes.fullimage : classes.image}
                    src={patchServerUrl(this.state.imgUrl)}
                    alt={this.props.title}
                    onError={this.onImgError}
                />;

            case "pdf":

                this.setPlaybackElement(null);
                return <PdfPanel file={patchServerUrl(url)} />;

            default:

                this.setPlaybackElement(null);

                const filename = url.replace(/^.*[\\/]/, '');
                const style = filename.length > 25 ? {fontSize: "10px"} : {};

                return <Button
                    variant="extendedFab"
                    aria-label="Delete"
                    className={classes.button}
                    style={style}
                    href={patchServerUrl(url)}
                    download
                >
                    <SaveIcon className={classes.extendedIcon}/> {filename}
                </Button>;
        }
    }
}

MediaPanel.propTypes = {
    url: PropTypes.string.isRequired,
    title: PropTypes.string,
    showControls: PropTypes.bool,
    autoplay: PropTypes.bool,
    playOnClick: PropTypes.bool,
    paused: PropTypes.bool,
    volume: PropTypes.number,
    restart: PropTypes.any,
    loop: PropTypes.bool
};

MediaPanel.defaultProps = {
    autoplay: false,
    showControls: true
};

const styles = theme => ({
    image: {
        maxWidth: "100%",
        maxHeight: "100%",
        objectFit: "contain"
    },
    fullimage: {
        display: "block",
        maxWidth: "100%",
        maxHeight: "100%",
        position: "fixed",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)"
    },
    other: {
        maxWidth: "100%",
        maxHeight: "100%"
    },
    fullsize: {
        width: "100%",
        height: "100%"
    },
    button: {
        maxWidth: "calc(100% - 10px)",
        overflow: "hidden",

    }
});

export default withStyles(styles)(MediaPanel);
