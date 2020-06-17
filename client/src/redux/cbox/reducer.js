/**
 * CBox redux reducer
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
    INIT_BOX, HALT_BOX, SET_MEDIA_URL, SET_BOX_PROPERTIES, SET_BOX_CONTENT, SET_BOX_SCREENSAVER, SHOW_SCREENSAVER, RESET_IDLE_TIMER,
    SHOW_CHAT_MESSAGE, SHOW_CHAT_INTERACTION, SHOW_CHAT_ANSWER, CLEAR_CHAT, SHOW_CHAT, SHOW_NOTIFICATION,
    PAUSE_PLAYBACK_ACTION, RESUME_PLAYBACK_ACTION, STOP_PLAYBACK_ACTION, SET_PLAYBACK_VOLUME_ACTION,
    SET_BOX_MENU_ACTION, SET_BOX_MENU_FLAGS_ACTION, SET_BOX_CONTEXT
} from "./consts";
import {
    CONTENT_MODE, CHAT_MODE
} from "./consts";


const initialState = {
    boxName: undefined,
    screenIndex: 0,
    language: "de", // TODO: change dynamically
    mode: undefined,
    chatOverlay: false,
    properties: {
        chat: {},
        menu: {}
    },
    playback: {
        content: undefined,
        referencedObjects: {},
        loop: false,
        restart: 0
    },
    backdrop: {
        content: undefined,
        referencedObjects: {},
        loop: false,
        restart: 0
    },
    context: {
        subjectQuantity: 10,
        subjects: [],
        referencedObjects: []
    },
    screensaver: {
        timeout: 0,
        content: undefined,
        referencedObjects: {}
    },
    idle: {
        time: new Date(),
        force: null
    },
    paused: false,
    volume: 100,
    chat: [],
    menus: {},
    interaction: undefined,
    notification: undefined,
    activity: {
        description: "",
        time: new Date()
    }
};


function replaceToggle(previousFlags, newFlags) {
    if (newFlags.visible === "toggle") {
        return {
            ...previousFlags,
            ...newFlags,
            visible: previousFlags ? !previousFlags.visible : true
        }
    }
    else {
        return {
            ...previousFlags,
            ...newFlags
        };
    }
}

function switchToMode(state, mode) {
    return {
        ...state,
        mode: mode,
        chatOverlay: false
    };
}

function switchToChat(state, forceChatMode = false) {
    const chatShared = !forceChatMode && state.properties.chat && state.properties.chat.display === 'shared';
    if (chatShared) {
        return {
            ...state,
            chatOverlay: true
        };
    }
    else {
        return {
            ...state,
            mode: CHAT_MODE,
            chatOverlay: false
        };
    }
}


export default function cboxReducer(state = initialState, action) {

    switch (action.type) {

        case INIT_BOX: {

            return {
                ...state,
                boxName: action.boxName,
                screenIndex: action.screenIndex || 0
            }
        }

        case HALT_BOX: {

            return initialState;
        }
        
        case SET_MEDIA_URL: {

            return {
                ...switchToMode(state, CONTENT_MODE),
                playback: {
                    content: {type: "mediaitem", fields: {url: action.url}},
                    loop: false,
                    referencedObjects: {},
                    restart: state.playback.restart + 1 // to make a change if the same content is set again
                },
                activity: {
                    description: "playing " + action.url,
                    time: new Date()
                }
            };
        }

        case SET_BOX_PROPERTIES: {

            return {
                ...state,
                properties: action.properties,
                menus: createMenusMap(action.properties.menu.menus),
                shortcuts: action.properties.shortcuts
            };
        }

        case SET_BOX_CONTENT: {

            if (action.backdrop) {
                return {
                    ...state,
                    backdrop: {
                        content: action.object,
                        loop: action.loop,
                        referencedObjects: createReferencedObjectsMap(action.referencedObjects),
                        restart: state.backdrop.restart + 1 // to make a change if the same content is set again
                    }
                };
            }
            else {
                return {
                    ...switchToMode(state, CONTENT_MODE),
                    playback: {
                        content: action.object,
                        loop: action.loop,
                        referencedObjects: createReferencedObjectsMap(action.referencedObjects),
                        restart: state.playback.restart + 1 // to make a change if the same content is set again
                    },
                    context: {
                        ...state.context,
                        subjectQuantity: getSubjectQuantity(action.object),
                        subjects: action.subjects || [],
                        referencedObjects: Array((action.subjects || []).length).fill([])
                    },
                    activity: {
                        description: "playing " + action.object.id,
                        time: new Date()
                    }
                };
            };
        }

        case SET_BOX_CONTEXT: {

            const referencedObjects = action.referencedObjects.map(
                referencedObjects => createReferencedObjectsMap(referencedObjects)
            );

            switch (action.operation) {
                case "append":
                    return {
                        ...state,
                        context: {
                            ...state.context,
                            subjects: [...state.context.subjects, ...action.subjects].slice(-state.context.subjectQuantity),
                            referencedObjects: [...state.context.referencedObjects, ...referencedObjects].slice(-state.context.subjectQuantity)
                        }
                    }
                case "insert":
                    return {
                        ...state,
                        context: {
                            ...state.context,
                            subjects: [...action.subjects, ...state.context.subjects].slice(0, state.context.subjectQuantity),
                            referencedObjects: [...referencedObjects, ...state.context.referencedObjects].slice(0, state.context.subjectQuantity)
                        }
                    }
                case "put":
                    let newSubjects = [...state.context.subjects];
                    let newReferencedObjects = [...state.context.referencedObjects];
                    for (let i = 0; i < action.subjects.length; ++i) {
                        newSubjects[action.index + i] = action.subjects[i];
                        newReferencedObjects[action.index + i] = referencedObjects[i];
                    }
                    return {
                        ...state,
                        context: {
                            ...state.context,
                            subjects: newSubjects,
                            referencedObjects: newReferencedObjects
                        }
                    }
                default:
                    return {
                        ...state,
                        context: {
                            ...state.context,
                            subjects: action.subjects,
                            referencedObjects: referencedObjects
                        }
                    }
                }
        }

        case SET_BOX_SCREENSAVER: {

            return {
                ...state,
                screensaver: {
                    ...state.screensaver,
                    timeout: action.screensaver.timeout,
                    content: action.screensaver.content,
                    referenced: action.screensaver.referenced
                }
            }
        }

        case SHOW_SCREENSAVER: {

            return {
                ...state,
                idle: {
                    ...state.idle,
                    force: new Date()
                }
            }
        }

        case RESET_IDLE_TIMER: {

            return {
                ...state,
                idle: {
                    ...state.idle,
                    time: new Date()
                }
            }
        }

        case SHOW_CHAT_MESSAGE: {

            return {
                ...switchToChat(state),
                chat: [...state.chat, {...action.message, own: false}],
                activity: {
                    description: "showing chat message",
                    time: new Date()
                }
            };
        }

        case SHOW_CHAT_INTERACTION: {

            return {
                ...switchToChat(state),
                chat: action.interaction.text ? [...state.chat, action.interaction] : state.chat,
                interaction: action.interaction,
                activity: {
                    description: "showing chat interaction",
                    time: new Date()
                }
            }
        }

        case SHOW_CHAT_ANSWER: {

            return {
                ...switchToChat(state),
                chat: [...state.chat, {...action.message, own: true}],
                interaction: undefined,
                activity: {
                    description: "showing chat answer",
                    time: new Date()
                }
            };
        }

        case CLEAR_CHAT: {

            return {
                ...state,
                chat: [],
                interaction: undefined,
                activity: {
                    description: "clearing chat",
                    time: new Date()
                }
            };
        }

        case SHOW_CHAT: {

            if (action.visible) return switchToChat(state, action.forceChatMode);
            else return {
                ...state,
                chatOverlay: false
            }
        }

        case SHOW_NOTIFICATION: {

            return {
                ...state,
                notification: action.text
            }
        }

        case PAUSE_PLAYBACK_ACTION: {

            return {
                ...state,
                paused: true
            };
        }

        case RESUME_PLAYBACK_ACTION: {

            return {
                ...state,
                paused: false
            };
        }

        case STOP_PLAYBACK_ACTION: {

            if (action.backdrop) {
                return {
                    ...state,
                    backdrop: {
                        ...state.backdrop,
                        content: null
                    }
                }
            }
            else {
                return {
                    ...state,
                    playback: {
                        ...state.playback,
                        content: null
                    }
                }
            }
        }

        case SET_PLAYBACK_VOLUME_ACTION: {
            return {
                ...state,
                volume: action.volume
            };
        }

        case SET_BOX_MENU_ACTION: {
            return {
                ...state,
                menus: {
                    ...state.menus,
                    [action.slot]: {
                        menu: action.menu,
                        flags: replaceToggle(state.menus[action.slot].flags || {}, action.flags),
                        referencedObjects: createReferencedObjectsMap(action.referencedObjects)
                    }
                }
            };
        }

        case SET_BOX_MENU_FLAGS_ACTION: {
            return {
                ...state,
                menus: {
                    ...state.menus,
                    [action.slot]: {
                        ...state.menus[action.slot],
                        flags: replaceToggle(state.menus[action.slot].flags, action.flags)
                    }
                }
            };
        }

        default:
            return state;
    }
}

function createReferencedObjectsMap(objects) {
    // generate map from list of objects
    let result = {};
    if (objects) {
        objects.forEach(item => {
            if (item) {
                result[item.id] = item;
            }
        });
    }
    return result;
}

function createMenuMap(menu) {
    return {
        ...menu,
        referencedObjects: createReferencedObjectsMap(menu.referencedObjects)
    };
}

function createMenusMap(menus) {
    let result = {};
    for (const slot in menus) {
        result[slot] = createMenuMap(menus[slot]);
    }
    return result;
}

function getSubjectQuantity(object) {
    if (object && object.type === "objectinfopanel") {
        return parseInt(object.fields.quantity) || 1;
    }
    else {
        return 10;
    }
}