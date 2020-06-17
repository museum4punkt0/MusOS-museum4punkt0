/**
 * types redux selectors
 * 
 * @author    Jens Gruschel
 * @copyright © 2019 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


import _ from "lodash";
import {toUserFriendlySecondsString} from "../../utils";


/**
 * select definition for a given object field
 * @param state         current state
 * @param objectTypeId  object type ID
 * @param fieldName     field of interest
 * @returns {Object}    field definition or undefined
 * @author Jens Gruschel
 */
export function selectFieldDefinition(state, objectTypeId, fieldName) {

    const fieldDefinitons = state.flatFieldDefinitions[objectTypeId];
    if (!fieldDefinitons) return undefined;
    return fieldDefinitons[fieldName];
}

/**
 * select type of a given object field
 * @param state         current state
 * @param objectTypeId  object type ID
 * @param fieldName     field of interest
 * @returns {String}    type of this field
 * @author Jens Gruschel
 */
export function selectFieldType(state, objectTypeId, fieldName) {

    // get field defintion and return actual value if not possible
    const fieldDefinition = selectFieldDefinition(state, objectTypeId, fieldName);
    if (!fieldDefinition) return undefined;

    // return default value
    return fieldDefinition.type;
}

function translateSpecialFieldName(specialFieldName) {
    switch (specialFieldName) {
        case "id": return "ID";
        case "imageurl": return "Bild";
        case "thumbnailurl": return "Bild";
        case "title": return "Titel";
        case "remarks": return "Bemerkungen";
        case "todo": return "zu erledigen";
        case "description": return "Beschreibung";
        case "objectaccess": return "Zugriff";
        case "mediainfo": return "Medien-Information";
        default: return specialFieldName;
    }
}

function translateOtherFieldName(fieldName) {
    if (fieldName.startsWith("#")) {
        return translateSpecialFieldName(fieldName.substr(1));
    }
    else {
        return fieldName;
    }   
}

/**
 * select (translated) name of a given object field
 * @param state         current state
 * @param objectTypeId  object type ID
 * @param fieldName     field of interest
 * @returns {String}    name of this field
 * @author Jens Gruschel
 */
export function selectFieldName(state, objectTypeId, fieldName) {

    // handle special fields
    if (fieldName.startsWith("#")) {
        return translateSpecialFieldName(fieldName.substr(1))
    }

    // return the last part directly if the object type is unknown
    if (!objectTypeId) {
        const lastDotPos = fieldName.lastIndexOf(".");
        const lastFieldName = (lastDotPos > 0) ? fieldName.substr(lastDotPos + 1) : fieldName;
        return translateOtherFieldName(lastFieldName);
    }

    // handle nested fields (dotPos > 0 to avoid empty field names)
    const dotPos = fieldName.indexOf(".");
    if (dotPos > 0) {
        const subFieldName = fieldName.substr(0, dotPos);
        const remainingFieldName = fieldName.substr(dotPos + 1);
        const fieldDefinition = selectFieldDefinition(state, objectTypeId, subFieldName);
        const subFieldTypeId = fieldDefinition && fieldDefinition.reftypes ? fieldDefinition.reftypes[0] : undefined;
        return selectFieldName(state, subFieldTypeId, remainingFieldName);
    }

    // get field defintion and return field name if not possible
    const fieldDefinition = selectFieldDefinition(state, objectTypeId, fieldName);
    if (!fieldDefinition) {
        const lastDotPos = fieldName.lastIndexOf(".");
        const lastFieldName = (dotPos > 0) ? fieldName.substr(lastDotPos + 1) : fieldName;
        return translateSpecialFieldName(lastFieldName);
    }

    // return default value
    return fieldDefinition.name || fieldName;
}

/**
 * select default value for a given object field
 * @param state         current state
 * @param objectTypeId  object type ID
 * @param fieldName     field of interest
 * @returns {*}         default value for this field
 * @author Jens Gruschel
 */
export function selectFieldDefaultValue(state, objectTypeId, fieldName) {

    // get field defintion and return actual value if not possible
    const fieldDefinition = selectFieldDefinition(state, objectTypeId, fieldName);
    if (!fieldDefinition) return undefined;

    // return default value
    return fieldDefinition.default;
}

/**
 * select value or default value for a given object field
 * @param state         current state
 * @param object        object of interest
 * @param fieldName     field of interest
 * @returns {*}         actual field value or default for this field
 * @author Jens Gruschel
 */
export function selectFieldValueOrDefault(state, object, fieldName) {

    // get actual value and return it, if present
    if (!object.fields) return undefined;
    const actualValue = object.fields[fieldName];
    if (actualValue !== undefined) return actualValue;

    // get field defintion and return actual value if not possible
    if (!object.type) return actualValue;
    const fieldDefinition = selectFieldDefinition(state, object.type, fieldName);
    if (!fieldDefinition) return actualValue;

    // return default value
    return fieldDefinition.default;
}

/**
 * select value or default value plus suffix or default suffix for a given object field
 * @param state         current state
 * @param object        object of interest
 * @param fieldName     field of interest
 * @returns {*}         actual field value or default for this field
 * @author Jens Gruschel
 */
export function selectFieldValueOrDefaultWithSuffix(state, object, fieldName, translate = null) {

    // get actual value + suffix and return both, if present
    if (!object.fields) return undefined;
    const actualValue = object.fields[fieldName];
    const actualSuffix = object.fields[fieldName + "__suffix"];
    if (actualValue !== undefined && actualSuffix) {
        if (translate) return translate(actualValue) + " " + actualSuffix;
        else return actualValue + " " + actualSuffix;
    }

    // get field defintion and return actual value + suffix if not possible
    if (!object.type) {
        if (translate) return actualSuffix ? translate(actualValue) + " " + actualSuffix : translate(actualValue);
        else return actualSuffix ? actualValue + " " + actualSuffix : actualValue;
    }
    const fieldDefinition = selectFieldDefinition(state, object.type, fieldName);
    if (!fieldDefinition) {
        if (translate) return actualSuffix ? translate(actualValue) + " " + actualSuffix : translate(actualValue);
        else return actualSuffix ? actualValue + " " + actualSuffix : actualValue;
    }

    // return actual or default value + suffix
    const suffix = actualSuffix || fieldDefinition.defaultsuffix;
    const value = actualValue !== undefined ? actualValue : fieldDefinition.default;
    if (translate) return value && suffix ? translate(value) + " " + suffix : translate(value);
    else return value && suffix ? value + " " + suffix : value;
}

/**
 * select all fields with default values for a given object type
 * @param state         current state
 * @param objectTypeId  object type ID
 * @returns {*}         fields with default values
 * @author Jens Gruschel
 */
export function selectFieldsWithDefaultValues(state, objectTypeId) {
    const fieldDefinitons = state.flatFieldDefinitions[objectTypeId];
    if (!fieldDefinitons) return {};
    let result = {};
    for (const fieldName in fieldDefinitons) {
        const fieldDefiniton = fieldDefinitons[fieldName];
        if (fieldDefiniton.default !== undefined) {
            result[fieldName] = fieldDefiniton.default;
        }
        if (fieldDefiniton.defaultsuffix !== undefined) {
            result[fieldName + "__suffix"] = fieldDefiniton.defaultsuffix;
        }
    }
    return result;
}

/**
 * select all fields with default values for a given object type
 * @param state         current state
 * @param types         array of type IDs
 * @returns [String]    array of type IDs including derived types
 * @author Jens Gruschel
 */
export function selectDerivedTypes(state, types) {
    return _.flatMap(types, typeId => {
        if (state.derivedTypes[typeId]) {
            if (state.typeDefinitions[typeId]) {
                // include type itself
                return [...state.derivedTypes[typeId], typeId]
            }
            else {
                // exclude type itself, because it is not really existing
                return state.derivedTypes[typeId]
            }
        }
        else {
            // return just the type itself
            return [typeId];
        }
    });
}

/**
 * select table field map for the given type IDs (which should be distinct)
 * @param state             current state
 * @param typeIds           array of unique type IDs
 * @returns {*}             map with table field IDs for each given type
 * @author Jens Gruschel
 */
export function selectTableFieldsMap(state, typeIds) {
    let result = {};
    for (const typeId of typeIds) {
        const typeDefiniton = state.typeDefinitions[typeId];
        if (typeDefiniton) {
            result[typeId] = typeDefiniton.fields.tablefields || [];
        }
    }
    return result;
}

/**
 * select value of given field, supporting references to other objects
 * @param state             current state
 * @param objectMap         map of objects involved
 * @param object            said object
 * @param fieldName         field name (may contain dots for sub fields)
 * @returns {*}             field value (may be string, number, bool, null, object etc.) or undefined
 * @author Jens Gruschel
 */
export function selectFieldValue(state, objectMap, object, fieldName, withSuffix, translate = null) {

    if (fieldName === "this") {
        return object;
    }

    if (fieldName.startsWith("#")) {
        if (fieldName === '#mediainfo') {
            const mediaInfo = object.mediainfo;
            if (!mediaInfo) return undefined;
            let fieldTexts = []
            if (mediaInfo.duration) {
                fieldTexts.push(toUserFriendlySecondsString(mediaInfo.duration))
            }
            if (mediaInfo.width && mediaInfo.height) {
                fieldTexts.push(mediaInfo.width + " × " + mediaInfo.height)
            }
            return fieldTexts.join(", ");
        }
        return object[fieldName.substr(1)];
    }

    if (!object.fields) {
        return undefined;
    }

    // handle nested fields (dotPos > 0 to avoid empty field names)
    const dotPos = fieldName.indexOf(".");
    if (dotPos > 0) {
        const objects = object.fields[fieldName.substr(0, dotPos)];
        if (!objects) {
            return undefined;
        }
        return objects.map(value => {
            if (_.isObject(value)) {
                // handle sub object
                return selectFieldValue(state, objectMap, value, fieldName.substr(dotPos + 1), withSuffix, translate);
            }
            else {
                // handle referenced object
                const referencedObject = objectMap[value];
                if (!referencedObject) {
                    return "?";
                }
                return selectFieldValue(state, objectMap, referencedObject, fieldName.substr(dotPos + 1), withSuffix, translate);
            }
        }).join(", ");
    }

    const fieldValue = object.fields[fieldName];
    if (_.isArray(fieldValue)) {
        if (fieldValue.length > 0) {
            return fieldValue.map(value => {
                if (_.isObject(value)) {
                    if (value.title) {
                        // return title if given
                        return translate ? translate(value.title) : value.title;
                    }
                    else {
                        // otherwise return object itself (might be a multi language object)
                        return translate ? translate(value) : value;
                    }
                }
                else {
                    return value;
                }
            }).join(", ");
        }
        else {
            return undefined;
        }
    }
    else if (withSuffix) {
        return selectFieldValueOrDefaultWithSuffix(state, object, fieldName, translate);
    }
    else {
        return translate ? translate(fieldValue) : fieldValue;
    }
}

/**
 * select title of given object, supporting references to other objects
 * @param state             current state
 * @param objectMap         map of objects involved
 * @param object            said object
 * @param translate         function used for translation
 * @returns {String}        translated object title
 * @author Jens Gruschel
 */
export function selectObjectTitle(state, objectMap, object, translate) {
    const typeDefinition = state.typeDefinitions[object.type];
    if (!typeDefinition) return undefined;
    const titleFields = typeDefinition.fields.titlefields;
    if (titleFields && titleFields.length > 0) {
        const parts = titleFields.map((fieldName) => {
            if (_.isObject(fieldName)) {
                // handle more complex definitions like text literals
                if (fieldName.text) return fieldName.text;
                else if (fieldName["switch"]) {
                    const value = object.fields[fieldName["switch"]]
                    const caseName = "case " + value;
                    if (fieldName[caseName] !== undefined) {
                        return fieldName[caseName] || "";
                    }
                    else {
                        return fieldName["else"] || "";
                    }
                }
                else return "";
            }
            else {
                // directly use the translated field value
                return selectFieldValue(state, objectMap, object, fieldName, true, translate) || "";
            }
        });
        return parts.join(" ").trim();
    }
    else {
        return typeDefinition.fields.name;
    }
}

/**
 * get a list of all object IDs referenced by the given object
 * @param {Object} state            current state
 * @param {Object} object           object of interest
 * @returns {Array}                 list of object IDs referenced by the given object
 * @author Jens Gruschel
 */
export function selectReferencedObjectIds(state, object) {

    if (!object.fields) return [];
    const fieldDefinitions = state.flatFieldDefinitions[object.type];
    if (!fieldDefinitions) return [];

    let result = [];
    for (const id in fieldDefinitions) {
        const fieldDefinition = fieldDefinitions[id];
        if (fieldDefinition.type === "medialist" || fieldDefinition.type === "reference") {
            // collect all references of this field (each field holds an array of references)
            const references = object.fields[id];
            if (references) {
                result.push(...references);
            }
        }
        else if (fieldDefinition.type === "element") {
            // recursively check all all elements (possibly with different types)
            const elements = object.fields[id];
            if (elements) {
                elements.forEach(element => {
                    result.push(...selectReferencedObjectIds(state, element));
                });
            }
        }
    } 
    return result;
}