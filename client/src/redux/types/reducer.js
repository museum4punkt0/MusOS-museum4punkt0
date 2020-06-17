/**
 * types redux reducer
 * 
 * @author    Jens Gruschel
 * @copyright © 2018 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


import {
    LOAD_TYPE_DEFINITIONS
} from './consts';


const initialState = {
    typeDefinitions: {},
    alphabeticalTypeDefinitions: [],
    flatFieldDefinitions: {},
    derivedTypes: {}
};


export default function typesReducer(state = initialState, action) {

    switch (action.type) {

        case LOAD_TYPE_DEFINITIONS: {

            return {
                ...state,
                typeDefinitions: createTypeDefinitionMap(action.definitions),
                alphabeticalTypeDefinitions: createSortedTypeDefinitonArray(action.definitions),
                flatFieldDefinitions: createFlatFieldDefinitionMap(action.definitions),
                derivedTypes: createDerivedTypeMap(action.definitions)
            };
        }

        default:
            return state;
    }
}

function createTypeDefinitionMap(definitions) {
    // generate map from list of type definitions
    let result = {};
    definitions.forEach(item => { result[item.fields.id] = item });
    return result;
}

function createSortedTypeDefinitonArray(definitions) {
    return definitions.filter(
        typeDefinition => !typeDefinition.fields.internal
    ).sort(
        (a, b) => a.fields.name.localeCompare(b.fields.name)
    )
}

function createDerivedTypeMap(definitions) {
    let result = {};
    definitions.forEach(item => {
        const parent = item.fields.parent;
        if (parent) {
            result[parent] = result[parent] ? [...result[parent], item.fields.id] : [item.fields.id];
        }
    });
    return result;
}

function createFlatFieldDefinitionMap(definitions) {
    // generate map from list of type definitions
    let result = {};
    definitions.forEach(item => {
        let fieldMap = {};
        forEachFieldDefinition(item.fields.definition.fieldsets, (id, def) => { fieldMap[id] = def });
        result[item.fields.id] = fieldMap;
    });
    return result;
}

function forEachFieldDefinition(fieldsets, func) {
    if (fieldsets) {
        fieldsets.forEach(fieldset => {
            if (fieldset.fields) {
                fieldset.fields.forEach(field => func(field.id, field))
            }
            if (fieldset.fieldsets) {
                forEachFieldDefinition(fieldset.fieldsets, func);
            }
        })
    }
}
