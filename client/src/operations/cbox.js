/**
 * CBox operations
 * 
 * @author    Jens Gruschel, Maurizio Tidei
 * @copyright © 2019 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


import {
    REST_CALL_REFRESH_BOX,
    REST_CALL_ANSWER_INTERACTION,
    REST_CALL_MENU_ACTION,
    REST_CALL_SHORTCUT_ACTION,
    REST_SERVER_BASE_URL
} from "../config";
import {fetchJSONActivity} from "./communication";
import {
    setBoxPropertiesAction, setBoxContentAction, setBoxScreensaverAction, showNotificationAction,
    showChatMessageAction, showChatInteractionAction, showChatAnswerAction, clearChatAction, showChatAction,
    pausePlaybackAction, resumePlaybackAction, stopPlaybackAction, setPlaybackVolumeAction,
    setBoxMenuAction, setBoxMenuFlagsAction, haltBoxAction, showScreensaverAction, resetIdleTimerAction,
    setMediaUrlAction, setBoxContextAction
} from "../redux/cbox/actions";
import {updateConfigurationAction} from "../redux/configuration/actions";


export function addSocketListener(socket) {

    return (dispatch, getState) => {
        socket.on('pingbox', (message) => {
            socket.emit('pongbox', {...message, 'boxname': getState().cbox.boxName});
            console.log("socket command: ping", Date.now(), message);
        });

        socket.on('reload', async (command) => {
            console.log("socket command: reload", Date.now(), command);
            window.location.reload();
        });

        socket.on('reset', async (command) => {
            console.log("socket command: reset", Date.now(), command);
            await socket.close();
            await socket.open();
            refreshBox()(dispatch, getState);
        });

        socket.on('halt', async (command) => {
            console.log("socket command: halt", Date.now(), command);
            dispatch(haltBoxAction());
        });

        socket.on('playmedia', (command) => {
            console.log("socket command: playmedia", Date.now(), command);
            dispatch(setMediaUrlAction(Date(command.time * 1000), command.url))
        });

        socket.on('playobject', (command) => {
            console.log("socket command: playobject", Date.now(), command);
            dispatch(setBoxContentAction(
                Date(command.time * 1000),
                command.object,
                command.loop,
                command.backdrop,
                command.referenced,
                command.subjects
            ));
        });

        socket.on('setcontext', (command) => {
            console.log("socket command: setcontext", Date.now(), command);
            dispatch(setBoxContextAction(command.subjects, command.referenced, command.operation));
        });

        socket.on('chatmessage', (command) => {
            console.log("socket command: chatmessage", Date.now(), command);
            dispatch(showChatMessageAction(command));
        });

        socket.on('chatinteraction', (command) => {
            console.log("socket command: chatinteraction", Date.now(), command);
            dispatch(showChatInteractionAction(command));
        });

        socket.on('clearchat', (command) => {
            console.log("socket command: clearchat", Date.now(), command);
            dispatch(clearChatAction());
        });

        socket.on('showchat', (command) => {
            console.log("socket command: showchat", Date.now(), command);
            dispatch(showChatAction(command.visible, command.forceChatMode));
        });

        socket.on('shownotification', (command) => {
            console.log("socket command: shownotification", Date.now(), command);
            dispatch(showNotificationAction(command.text));
        });

        socket.on('pause', (command) => {
            console.log("socket command: pause", Date.now(), command);
            dispatch(pausePlaybackAction());
        });

        socket.on('resume', (command) => {
            console.log("socket command: resume", Date.now(), command);
            dispatch(resumePlaybackAction());
        });

        socket.on('stop', (command) => {
            console.log("socket command: stop", Date.now(), command);
            dispatch(stopPlaybackAction(command.backdrop));
        });

        socket.on('setvolume', (command) => {
            console.log("socket command: setvolume", Date.now(), command);
            dispatch(setPlaybackVolumeAction(command.volume));
        });
        
        socket.on('changemenu', (command) => {
            console.log("socket command: changemenu", Date.now(), command);
            dispatch(setBoxMenuAction(command.slot, command.menu, {visible: command.visible, context: command.context}, command.referencedObjects));
        });

        socket.on('showmenu', (command) => {
            console.log("socket command: showmenu", Date.now(), command);
            dispatch(setBoxMenuFlagsAction(command.slot, {"visible": command.visible}));
        });

        socket.on('showscreensaver', (command) => {
            console.log("socket command: showscreensaver", Date.now(), command);
            dispatch(showScreensaverAction());
        });

        socket.on('resetidletimer', (command) => {
            console.log("socket command: resetidletimer", Date.now(), command);
            dispatch(resetIdleTimerAction());
        });
    }
}

export function refreshBox() {

    return async (dispatch, getState) => {

        try {
            const state = getState();
            const { authorization } = state;
            const boxName = state.cbox.boxName;
    
            const json = await fetchJSONActivity(dispatch, "refreshing CBox",
                REST_SERVER_BASE_URL + REST_CALL_REFRESH_BOX.path.replace("<cbox>", boxName), {
                    method: REST_CALL_REFRESH_BOX.method,
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer " + authorization.accessToken
                    }
                }
            );
    
            const now = Date.now();
            const content = json.content[0];
            const referenced = json.referenced || [];
            const properties = json.properties;
            const configuration = json.configuration;
            const screensaver = json.screensaver;

            dispatch(updateConfigurationAction(configuration));
            dispatch(setBoxPropertiesAction(properties));

            if (screensaver) {
                dispatch(setBoxScreensaverAction(screensaver));
            }

            console.log("refreshBox: content:", content, " referenced:", referenced);
            if (content) {
                dispatch(setBoxContentAction(now, content, true, false, referenced));
            }
        }
        catch (error) {
            console.log("refresh error:", error);
        }
    }
}

export function answerInteraction(scene_id, index, answer, text, context) {

    return async (dispatch, getState) => {

        dispatch(showChatAnswerAction({text: text}));

        try {
            const state = getState();
            const { authorization } = state;
            const boxName = state.cbox.boxName;
            var path = REST_CALL_ANSWER_INTERACTION.path.replace(
                "<scene_id>", scene_id
            ).replace(
                "<index>", index
            ).replace(
                "<answer>", answer
            ).replace(
                "<cbox>", boxName
            );

            await fetchJSONActivity(dispatch, "answering interaction",
                REST_SERVER_BASE_URL + path, {
                    method: REST_CALL_ANSWER_INTERACTION.method,
                    body: JSON.stringify({context: context}),
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer " + authorization.accessToken
                    }
                }
            );
        }
        catch (error) {
            console.log("interaction error:", error);
        }
    }
}

export function triggerMenuAction(menuId, index, context) {

    return async (dispatch, getState) => {

        try {
            const state = getState();
            const { authorization } = state;
            const boxName = state.cbox.boxName;
            var path = REST_CALL_MENU_ACTION.path.replace(
                "<menu_id>", menuId
            ).replace(
                "<index>", index
            ).replace(
                "<cbox>", boxName
            );

            await fetchJSONActivity(dispatch, "triggering menu",
                REST_SERVER_BASE_URL + path, {
                    method: REST_CALL_MENU_ACTION.method,
                    body: JSON.stringify({context: context}),
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer " + authorization.accessToken
                    }
                }
            );
        }
        catch (error) {
            console.log("menu error:", error);
        }
    }
}

export function triggerShortcutAction(index, context) {

    return async (dispatch, getState) => {

        try {
            const state = getState();
            const { authorization } = state;
            const boxName = state.cbox.boxName;
            var path = REST_CALL_SHORTCUT_ACTION.path.replace(
                "<index>", index
            ).replace(
                "<cbox_name>", boxName
            );

            await fetchJSONActivity(dispatch, "triggering shortcut",
                REST_SERVER_BASE_URL + path, {
                    method: REST_CALL_SHORTCUT_ACTION.method,
                    body: JSON.stringify({context: context}),
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer " + authorization.accessToken
                    }
                }
            );
        }
        catch (error) {
            console.log("shortcut error:", error);
        }
    }
}