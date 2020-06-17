/**
 * types redux actions
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
} from "./consts";


export const loadTypeDefinitionsSuccessAction = (definitions) => ({
    type: LOAD_TYPE_DEFINITIONS,
    definitions: definitions
});
