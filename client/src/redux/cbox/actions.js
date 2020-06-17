/**
 * CBox redux actions
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
    SET_MEDIA_URL, INIT_BOX, HALT_BOX, SET_BOX_PROPERTIES, SET_BOX_CONTENT, SET_BOX_SCREENSAVER, SHOW_SCREENSAVER, RESET_IDLE_TIMER,
    SHOW_CHAT_MESSAGE, SHOW_CHAT_INTERACTION, SHOW_CHAT_ANSWER, CLEAR_CHAT, SHOW_CHAT, SHOW_NOTIFICATION,
    PAUSE_PLAYBACK_ACTION, RESUME_PLAYBACK_ACTION, STOP_PLAYBACK_ACTION, SET_PLAYBACK_VOLUME_ACTION,
    SET_BOX_MENU_ACTION, SET_BOX_MENU_FLAGS_ACTION, SET_BOX_CONTEXT
} from "./consts";


export const initBoxAction = (boxName, screenIndex) => ({
    type: INIT_BOX,
    boxName: boxName,
    screenIndex: screenIndex
});

export const haltBoxAction = () => ({
    type: HALT_BOX
});

export const setMediaUrlAction = (time, url) => ({
    type: SET_MEDIA_URL,
    time: time,
    url: url
});

export const setBoxPropertiesAction = (properties) => ({
    type: SET_BOX_PROPERTIES,
    properties: properties
});

export const setBoxContentAction = (time, object, loop, backdrop, referencedObjects, subjects) => ({
    type: SET_BOX_CONTENT,
    time: time,
    object: object,
    loop: loop,
    backdrop: backdrop,
    referencedObjects: referencedObjects,
    subjects: subjects
});

export const setBoxContextAction = (subjects, referencedObjects, operation, index = 0) => ({
    type: SET_BOX_CONTEXT,
    subjects: subjects,
    referencedObjects: referencedObjects,
    operation: operation,
    index: index
});

export const setBoxScreensaverAction = (screensaver) => ({
    type: SET_BOX_SCREENSAVER,
    screensaver: screensaver
});

export const showScreensaverAction = () => ({
    type: SHOW_SCREENSAVER
})

export const resetIdleTimerAction = () => ({
    type: RESET_IDLE_TIMER
});

export const showChatMessageAction = (message) => ({
    type: SHOW_CHAT_MESSAGE,
    message: message
});

export const showChatInteractionAction = (interaction) => ({
    type: SHOW_CHAT_INTERACTION,
    interaction: interaction
});

export const showChatAnswerAction = (message) => ({
    type: SHOW_CHAT_ANSWER,
    message: message
});

export const clearChatAction = () => ({
    type: CLEAR_CHAT
});

export const showChatAction = (visible, forceChatMode) => ({
    type: SHOW_CHAT,
    visible: visible,
    forceChatMode: forceChatMode
});

export const showNotificationAction = (text) => ({
    type: SHOW_NOTIFICATION,
    text: text
});

export const pausePlaybackAction = () => ({
    type: PAUSE_PLAYBACK_ACTION
});

export const resumePlaybackAction = () => ({
    type: RESUME_PLAYBACK_ACTION
});

export const stopPlaybackAction = (backdrop) => ({
    type: STOP_PLAYBACK_ACTION,
    backdrop: backdrop
});

export const setPlaybackVolumeAction = (volume) => ({
    type: SET_PLAYBACK_VOLUME_ACTION,
    volume: volume
});

export const setBoxMenuAction = (slot, menu, flags, referencedObjects) => ({
    type: SET_BOX_MENU_ACTION,
    slot: slot,
    menu: menu,
    flags: flags,
    referencedObjects: referencedObjects
});

export const setBoxMenuFlagsAction = (slot, flags) => ({
    type: SET_BOX_MENU_FLAGS_ACTION,
    slot: slot,
    flags: flags
});
