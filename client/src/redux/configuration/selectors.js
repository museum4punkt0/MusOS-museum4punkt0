/**
 * configuration redux selectors
 * 
 * @author    Jens Gruschel
 * @copyright © 2019 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


/**
 * select list of supported languages
 * @param state         current state
 * @returns [String]    list of supported language codes
 * @author Jens Gruschel
 */
export function selectSupportedLanguages(state) {
    return state.active.supportedLanguages || ["de", "en"];
}

/**
 * select translation for given value
 * @param state         current state
 * @param value         value
 * @param language      language code
 * @returns String      translation for given langauge
 * @author Jens Gruschel
 */
export function selectTranslation(state, value, language = null, fallback = true) {
    if (value instanceof Object) {
        if (Object.keys(value).length === 0) return ""; // objects empty by intention result in empty strings
        const result = value[language || state.active.defaultLanguage];
        if (result) return result;
        if (fallback && state.active.fallbackLanguages) {
            for (let alternativeLanguage of state.active.fallbackLanguages) {
                const alternativeTranslation = value[alternativeLanguage];
                if (alternativeTranslation) return alternativeTranslation;
            }
        }
        return undefined;
    }
    else {
        // no translation available
        return value;
    }
}

/**
 * select value for a given user settings field
 * @param state         current state
 * @param fieldId       field ID
 * @returns {*}         user settings value
 * @author Jens Gruschel
 */
export function selectUserSetting(state, fieldId) {
    return state.userSettings.fields[fieldId];
}