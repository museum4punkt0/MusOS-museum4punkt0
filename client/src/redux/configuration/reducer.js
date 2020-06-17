/**
 * configuration redux reducer
 * 
 * @author    Jens Gruschel
 * @copyright © 2019 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


import {
    LOAD_CONFIGURATION, UPDATE_CONFIGURATION, LOAD_USER_SETTINGS, CHANGE_USER_SETTING
} from "./consts";


const initialState = {
    active: {
        defaultLanguage: "de",
        fallbackLanguages: ["en", "de"],
        logReduxActions: false,
        logReduxState: false,
        theme: "musos"
    },
    userSettings: {
        fields: {}
    }
};

export default function configurationReducer(state = initialState, action) {

    switch (action.type) {

        case LOAD_CONFIGURATION:
        case UPDATE_CONFIGURATION: {

            return {
                ...state,
                active: {
                    ...state.active,
                    ...action.configuration
                }
            };
        }

        case LOAD_USER_SETTINGS: {

            return {
                ...state,
                userSettings: action.settings
            };
        }

        case CHANGE_USER_SETTING: {
            return {
                ...state,
                userSettings: {
                    ...state.userSettings,
                    fields: {
                        ...state.userSettings.fields,
                        [action.fieldId]: action.value
                    }
                }
            };
        }

        default:
            return state;
    }
}
