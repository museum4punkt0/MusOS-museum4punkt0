/**
 * authorization redux reducer
 * 
 * @author    Jens Gruschel
 * @copyright © 2018 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


import {LOGIN_SUCCESS, LOGOUT} from "./consts";


const initialState = {
    accessToken: undefined
};


export default function authorizationReducer(state = initialState, action) {

    switch(action.type) {

        case LOGIN_SUCCESS:

            return {
                ...state,
                accessToken: action.accessToken
            };

        case LOGOUT:

            return initialState;

        default:
            return state;
    }
}
