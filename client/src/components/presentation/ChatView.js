/**
 * ChatView React component
 * 
 * @author    Jens Gruschel, Maurizio Tidei
 * @copyright © 2019 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
*/


import React from 'react';
import {connect} from 'react-redux';
import {withStyles} from "@material-ui/core";
import classNames from 'classnames';

import Button from '@material-ui/core/Button';
import MediaPanel from "../base/MediaPanel";
import Avatar from '@material-ui/core/Avatar';

import {answerInteraction} from "../../operations/cbox";
import {getMediaType} from "../../utils";
import {selectTranslation} from "../../redux/configuration/selectors";


function getTextClass(text) {
    if (text.length === 1) return "chat-text-large";
    else if (text.length >= 500) return "chat-text-small";
    else return "chat-text-normal";
}


/**
 * ChatView
 *
 * @author Jens Gruschel, Maurizio Tidei
 */
class ChatView extends React.Component {

    constructor(props) {
        super(props);
        this.messagesEnd = React.createRef();
    }

    componentDidMount() {
        this.scrollToBottom();
        //TODO: Quick workaround, find a solution for scrolling to the bottom after an image is really loaded!
        setTimeout(
            function() {
                this.scrollToBottom();
            }
            .bind(this),
            1000
        );
    }

    componentDidUpdate() {
        this.scrollToBottom();
        setTimeout(
            function() {
                this.scrollToBottom();
            }
            .bind(this),
            1000
        );
    }

    scrollToBottom = () => {
        if (this.messagesEnd && this.messagesEnd.current) {
            this.messagesEnd.current.scrollIntoView({ behavior: 'smooth' });
        }
    };

    render() {

        const {classes} = this.props;

        const {backgroundMediaUrl} = this.props.chatProperties;
        const hasBackgroundVideo = backgroundMediaUrl && getMediaType(backgroundMediaUrl) === "video";
        const hasBackgroundImage = backgroundMediaUrl && !hasBackgroundVideo;

        const backgroundStyle = {
            position: "absolute",
            top: 0,
            bottom: 0,
            left: 0,
            right: 0,
            // height: "100%",
            backgroundImage: hasBackgroundImage && "url(" + backgroundMediaUrl + ")",
            backgroundPosition: "center",
            backgroundRepeat: "no-repeat",
            backgroundSize: "cover"
        };

        const backgroundVideoElement = hasBackgroundVideo &&
            <video autoPlay loop id="bgVideo" style={{
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

        return (
            <div className={classNames(classes.chatFrame, this.props.overlay ? "chat-overlay" : "chat-frame")}>
                <style>
                    {this.props.chatProperties.stylesheet}
                </style>
                <div style={backgroundStyle} id="chat">
                    {backgroundVideoElement}
                    <div className="chat-image-A" />
                    <div className="chat-image-B" />
                    <div className="chat">
                        <div className={classes.chat}>
                            {
                                this.props.chat.map((message, index) => this.createMessageElement(message, index))
                            }
                            {
                                this.createInteractionControl()
                            }
                        </div>
                        <div key="end" ref={this.messagesEnd}/>
                    </div>
                </div>
            </div>
        );
    }

    createMessageElement(message, index) {

        const {classes} = this.props;

        if (message.own) {
            return <div key={message.time} className={classNames(classes.message, classes.ownMessage, "chat-message", "own-message")}>
                <div className={classNames(classes.bubbleContainer, classes.ownBubbleContainer)}>
                    <div className={classNames(classes.bubble, classes.ownBubble, "chat-bubble")}>
                        <section className={getTextClass(message.text)}>{this.props.translate(message.text)}</section>
                    </div>
                    <div className={classNames(classes.arrowRight, "chat-arrow-right")}></div>
                </div>
            </div>;
        }
        else {
            const avatar = message.avatar || this.props.chatProperties.avatar || {};
            return <div key={message.time} className={classNames(classes.message, classes.otherMessage, "chat-message", "other-message")}>
                <div className={classNames(classes.avatarContainer, "chat-avatar")}>
                    {avatar.imageurl && <Avatar src={avatar.imageurl} alt={avatar.name || "avatar"} className={classes.avatar}/>}
                </div>
                <div className={classNames(classes.bubbleContainer, classes.otherBubbleContainer)}>
                    <div className={classNames(classes.bubble, classes.otherBubble, "chat-bubble")}>
                        {avatar.name && <header>{avatar.name}</header>}
                        {message.objects && message.objects.map((obj, index) => {
                            return <div key={index} className={classes.chatMedia}><MediaPanel
                                url={obj.url}
                                autoplay={true}
                                showControls={true}
                                full={false}
                                loop={false}
                                paused={false}
                            /></div>;
                        })}
                        <section className={getTextClass(message.text)}>{this.props.translate(message.text)}</section>
                    </div>
                    <div className={classNames(classes.arrowLeft, "chat-arrow-left")}></div>
                </div>
            </div>;
        }
    }

    createInteractionControl() {

        const {classes, interaction} = this.props;
        if (!interaction) return null;

        return <div className={classNames(classes.answers, "chat-interaction")}>
        {
            interaction.answers.map(
                (answer, index) => {
                    const text = this.props.translate(answer);
                    return text && <Button
                        key={index}
                        variant="contained"
                        color="primary"
                        className={classNames(classes.button, "chat-button")}
                        style={{ fontSize: this.props.normalFontSize }}
                        onClick={() => this.props.answerInteraction(interaction.origin.scene, interaction.origin.index,
                            index, text, interaction.context)}
                    >
                        {text}
                    </Button>;
                }
            )
        }
        </div>;
    }
}

const styles = theme => ({
    chatFrame: {
        position: "absolute",
        left: 0,
        right: 0,
        top: 0,
        bottom: 0
    },
    chat: {
        //position: "absolute",
        //bottom: 0,
        overflow: "hidden",
        paddingBottom: 20
    },
    message: {
        position: "relative",
        marginTop: 20,
        marginBottom: 0,
        marginLeft: 40,
        marginRight: 40,
        whiteSpace: "nowrap"
    },
    otherMessage: {
        textAlign: "left"
    },
    ownMessage: {
        textAlign: "right"
    },
    bubbleContainer: {
        display: "inline-block",
        position: "relative"
    },
    otherBubbleContainer: {
    },
    ownBubbleContainer: {
        marginLeft: 300
    },
    bubble: {
        position: "relative",
        overflow: "hidden",
        whiteSpace: "pre-wrap",
        minHeight: 30,
        borderRadius: 15,
        padding: 20
    },
    otherBubble: {
        backgroundColor: "#fff",
        color: "#000"
    },
    ownBubble: {
        backgroundColor: "#fff",
        color: "#000"
    },
    arrowLeft: {
        position: "absolute",
        right: "100%",
        bottom: 15,
        height: 0,
        width: 0,
        border: "solid transparent",
        borderRightColor: "#fff",
        borderWidth: 15,
        marginTop: -15
    },
    arrowRight: {
        position: "absolute",
        left: "100%",
        bottom: 15,
        height: 0,
        width: 0,
        border: "solid transparent",
        borderLeftColor: "#fff",
        borderWidth: 15,
        marginTop: -15
    },
    avatarContainer: {
        display: "inline-block",
        width: 120,
        height: 120,
        marginRight: 20
    },
    avatar: {
        width: "100%",
        height: "100%"
    },
    answers: {
        position: "relative",
        float: "right",
        marginTop: 0,
        marginBottom: 20,
        marginLeft: 40,
        marginRight: 40
    },
    button: {
        margin: 8,
        textTransform: 'none',
        boxShadow: 'none',
        backgroundColor: "#ddd",
        color: "#000",
        border: '1px solid',
        borderColor: "#000",
        '&:hover': {
            backgroundColor: "#fff"
        }
    },
    chatMedia: {
        display: "inline",
        marginRight: 8
    }
});

const mapStateToProps = state => {
    return {
        chatProperties: state.cbox.properties.chat,
        chat: state.cbox.chat.slice(-100),
        interaction: state.cbox.interaction,
        translate: (value) => selectTranslation(state.configuration, value, state.cbox.language)
    };
};

export default connect(mapStateToProps, {answerInteraction})(withStyles(styles)(ChatView));