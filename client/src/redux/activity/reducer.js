/**
 * activity redux reducer
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
    START_ACTIVITY,
    FINISH_ACTIVITY,
} from "./consts";


const initialState = {
    activities: {}
};


export default function activityReducer(state = initialState, action) {

    switch (action.type) {

        case START_ACTIVITY: {

            let newActivites = {...state.activities};
            newActivites[action.activityId] = action.description;

            return {
                ...state,
                activities: newActivites
            };
        }

        case FINISH_ACTIVITY: {

            let newActivites = {...state.activities};
            delete newActivites[action.activityId];

            return {
                ...state,
                activities: newActivites
            };
        }

        default:
            return state;
    }
}
