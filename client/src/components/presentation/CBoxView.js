/**
 * CBoxView React component
 * 
 * @author    Maurizio Tidei, Jens Gruschel
 * @copyright © 2019 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


// React
import React from 'react';
import {connect} from 'react-redux';

// Material-UI
import {withStyles} from "@material-ui/core";

// 3rd party
import { DndProvider } from 'react-dnd'
import MultiBackend, { Preview } from 'react-dnd-multi-backend';
import HTML5toTouch from 'react-dnd-multi-backend/dist/esm/HTML5toTouch'; // or any other pipeline

// application
import ContentView from "./ContentView";
import ChatView from "./ChatView";
import MenuFrame from "./MenuFrame";
import NotificationBar from "./NotificationBar"
import MediaPanel from "../base/MediaPanel";
import {
    CONTENT_MODE, CHAT_MODE
} from "../../redux/cbox/consts";
import {selectTranslation} from "../../redux/configuration/selectors";
import {GlobalHotKeys} from "react-hotkeys";
import _ from "lodash";
import {triggerShortcutAction} from "../../operations/cbox";
import {DraggableMenuObjectPreview} from "./DraggableMenuObject";


/**
 * CBoxView
 *
 * @author Maurizio Tidei, Jens Gruschel
 */
class CBoxView extends React.Component {

    isVisible = null;
    idleTime = new Date();

    state = {
        screensaverRunning: false
    }

    handleEvent(event) {
        switch (event.type) {
            case 'focus':
                this.isVisible = true;
                break;
            case 'blur':
                this.isVisible = false;
                break;
            case 'keydown':
            case 'keyup':
            case 'mousemove':
            case 'mousedown':
            case 'mouseup':
            case 'wheel':
                this.resetIdleTimer();
                break;
            default:
                break;
        }
    }

    componentDidMount() {
        this.aliveTimer = setInterval(() => {this.aliveTick()}, 5000);
        this.idleTimer = setInterval(() => {this.idleTick()}, 1000);
        window.addEventListener('focus', this);
        window.addEventListener('blur', this);
        window.addEventListener('keydown', this);
        window.addEventListener('keyup', this);
        window.addEventListener('mousemove', this);
        window.addEventListener('mousedown', this);
        window.addEventListener('mouseup', this);
        window.addEventListener('wheel', this);
    }

    componentWillUnmount() {
        window.removeEventListener('focus', this);
        window.removeEventListener('blur', this);
        window.removeEventListener('keydown', this);
        window.removeEventListener('keyup', this);
        window.removeEventListener('mousemove', this);
        window.removeEventListener('mousedown', this);
        window.removeEventListener('mouseup', this);
        window.removeEventListener('wheel', this);
        clearInterval(this.idleTimer);
        clearInterval(this.aliveTimer);
    }

    componentDidUpdate(prevProps) {
        if (!this.state.screensaverRunning) {
            if (this.props.idleForce && this.props.idleForce !== prevProps.idleForce) {
                this.setState({screensaverRunning: true})
            }
        }
        else {
            if (this.props.idleTime && this.props.idleTime !== prevProps.idleTime) {
                this.setState({screensaverRunning: false})
            }
        }
    }

    aliveTick() {
        if (this.props.onAlive) this.props.onAlive(this.isVisible, this.props.activityDescription);
    }

    idleTick() {
        if (!this.state.screensaverRunning && this.props.screensaverTimeout) {
            const idleTime = (this.props.idleTime && this.props.idleTime > this.idleTime) ? this.props.idleTime : this.idleTime;
            const milliseconds = new Date() - idleTime;
            if (milliseconds * 0.001 >= this.props.screensaverTimeout) {
                this.setState({screensaverRunning: true});
            }
        }
    }

    resetIdleTimer() {
        this.idleTime = new Date();
        if (this.state.screensaverRunning) {
            this.setState({screensaverRunning: false});
        }
    }

    render() {

        const menuProperties = this.props.menuProperties;
        const menuStylesheet = menuProperties ? menuProperties.stylesheet : null;

        let shortcutsKeyMap = {};
        let shortcutsHandlers = {};
        for (const i in this.props.shortcuts) {
            shortcutsKeyMap[i] = this.props.shortcuts[i];
            shortcutsHandlers[i] = event => {
                this.props.triggerShortcutAction(i);
            }
        }

        const hotkeys = !_.isEmpty(shortcutsKeyMap) && <GlobalHotKeys keyMap={shortcutsKeyMap} handlers={shortcutsHandlers}/>;

        if (this.state.screensaverRunning) {
            return (
                <div className={this.props.classes.screen} style={{backgroundColor: this.props.boxProperties.backgroundColor || '#000000'}}>
                    {this.renderScreensaver()}
                    {hotkeys}
                </div>
            );
        }

        // render content and menus
        // (menu B first, so menu A is in front of menu B naturally without ordering)        
        return <DndProvider backend={MultiBackend} options={HTML5toTouch}>
            <div className={this.props.classes.screen} style={{backgroundColor: this.props.boxProperties.backgroundColor || '#000000'}}>
                <style>
                    {menuStylesheet}
                </style>
                {this.renderBackdrop()}
                {this.renderContent()}
                {this.renderMenu("B", "menu-b", this.props.menus.B)}
                {this.renderMenu("A", "menu-a", this.props.menus.A)}
                {hotkeys}
                <Preview>
                    <DraggableMenuObjectPreview className={"menuobject"}/>
                </Preview>
            </div>
        </DndProvider>;
    }

    renderScreensaver() {

        const {classes, screensaver, notification, screenIndex} = this.props;

        return <div id="cbox-background" className={classes.background}>
            <div id="cbox-screensaver" className={classes.screensaver}>
                <ContentView
                    screenIndex={screenIndex}
                    content={screensaver.content}
                    referencedObjects={screensaver.referencedObjects}
                    loop={true}
                />
            </div>
            <NotificationBar text={notification} />
        </div>;
    }

    renderBackdrop() {

        const {content} = this.props.backdrop;

        if (content && content.fields && content.type === "mediaitem") {
            return <MediaPanel
                style={{ width: 0, height: 0 }}
                url={content.fields.url}
                restart={this.props.backdrop.restart}
                autoplay={true}
                showControls={false}
                loop={this.props.backdrop.loop}
                volume={this.props.volume}
            />;
        }
        else {
            return null;
        }
    }

    renderContent() {

        const {classes, chatOverlay, notification, screenIndex} = this.props;

        switch (this.props.mode) {

            case CONTENT_MODE:

                const playback = this.props.playback;

                return <div id="cbox-background" className={classes.background}>
                    <div id="cbox-content" className={classes.content}>
                        <ContentView
                            screenIndex={screenIndex}
                            content={playback.content}
                            referencedObjects={playback.referencedObjects}
                            navigationIndex={playback.navigationIndex}
                            loop={playback.loop}
                            paused={this.props.paused}
                            volume={this.props.volume}
                            restart={playback.restart}
                        />
                    </div>
                    {chatOverlay && <ChatView overlay={true} />}
                    <NotificationBar text={notification} />
                </div>;

            case CHAT_MODE:

                return <div id="cbox-background" className={classes.background}>
                    <ChatView overlay={false} />
                    <NotificationBar text={notification} />
                </div>;

            default:

                return <div id="cbox-background" className={classes.background}>
                    {chatOverlay && <ChatView overlay={true} />}
                    <NotificationBar text={notification} />
                </div>;
        }
    }

    restrictMenuVisibility(visibility, visible) {
        switch (visibility) {
            case "arbitrary": return visible;
            case "chatonly": return visible && this.props.mode === CHAT_MODE;
            case "contentonly": return visible && this.props.mode === CONTENT_MODE;
            case "mediaonly": return visible && this.props.mode === CONTENT_MODE && this.props.playbackContentType === "mediaitem";
            case "slidesonly": return visible && this.props.mode === CONTENT_MODE && this.props.playbackContentType === "textslide";
            case "htmlonly": return visible && this.props.mode === CONTENT_MODE && this.props.playbackContentType === "htmlcontent";
            default: return visible;
        }
    }

    renderMenu(slot, elementId, menu) {
        if (menu && menu.menu && menu.menu.fields) {
            const visible = this.restrictMenuVisibility(menu.menu.fields.visibility, menu.flags.visible);
            return <MenuFrame
                slot={slot}
                elementId={elementId}
                menu={menu.menu}
                flags={{...menu.flags, visible: visible}}
                referencedObjects={menu.referencedObjects}
            />;
        }
        else {
            return null;
        }
    }
}

const styles = theme => ({
    screen: {
        position: "absolute",
        top: 0,
        bottom: 0,
        left: 0,
        right: 0,
        display: "flex",
        flexDirection: "row",
        flexWrap: "nowrap",
        justifyContent: "space-between",
        alignItems: "stretch"
    },
    background: {
        position: "relative",
        width: "100%",
        height: "100%",
        overflow: "hidden"
    },
    screensaver: {
        position: "sticky", // avoid scrolling with overlay chat
        top: 0,
        height: "100%"
    },
    content: {
        position: "sticky", // avoid scrolling with overlay chat
        top: 0,
        height: "100%"
    }
});

const mapStateToProps = state => {

    const translate = (value) => selectTranslation(state.configuration, value, state.cbox.language);

    const playback = state.cbox.playback;

    return {
        screenIndex: state.cbox.screenIndex,
        boxProperties: state.cbox.properties || {},
        chatProperties: state.cbox.properties.chat || {},
        menuProperties: state.cbox.properties.menu || {},
        mode: state.cbox.mode,
        playback: playback,
        playbackContentType: playback && playback.content ? playback.content.type : undefined,
        paused: state.cbox.paused,
        volume: state.cbox.volume,
        chatOverlay: state.cbox.chatOverlay || (state.cbox.properties.chat && state.cbox.properties.chat.display === 'permanent'),
        backdrop: state.cbox.backdrop,
        notification: translate(state.cbox.notification),
        menus: state.cbox.menus || {},
        activityDescription: state.cbox.activity.description,
        screensaver: state.cbox.screensaver,
        screensaverTimeout: state.cbox.screensaver.timeout || 0,
        idleTime: state.cbox.idle.time,
        idleForce: state.cbox.idle.force,
        shortcuts: state.cbox.shortcuts
    };
};

export default connect(mapStateToProps, {triggerShortcutAction})(withStyles(styles)(CBoxView));