/**
 * redux root reducer
 * 
 * @author    Maurizio Tidei, Jens Gruschel
 * @copyright © 2018 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


import { combineReducers } from 'redux';
import typesReducer from "./types/reducer";
import activityReducer from "./activity/reducer";
import authorizationReducer from "./authorization/reducer";
import cboxReducer from "./cbox/reducer";
import configurationReducer from "./configuration/reducer";


const rootReducer = combineReducers({
    types: typesReducer,
    activity: activityReducer,
    authorization: authorizationReducer,
    cbox: cboxReducer,
    configuration: configurationReducer
});

export default rootReducer