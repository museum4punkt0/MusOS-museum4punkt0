/**
 * configuration redux actions
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


export const loadConfigurationAction = (configuration) => ({
    type: LOAD_CONFIGURATION,
    configuration: configuration
});

export const updateConfigurationAction = (configuration) => ({
    type: UPDATE_CONFIGURATION,
    configuration: configuration
});

export const loadUserSettingsAction = (settings) => ({
    type: LOAD_USER_SETTINGS,
    settings: settings
});

export const changeUserSettingAction = (fieldId, value) => ({
    type: CHANGE_USER_SETTING,
    fieldId: fieldId,
    value: value
});
