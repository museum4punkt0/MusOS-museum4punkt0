/**
 * activity redux actions
 * 
 * @author    Jens Gruschel
 * @copyright © 2018 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


import {START_ACTIVITY, FINISH_ACTIVITY} from "./consts";


export const startActivityAction = (activityId, description) => ({
    type: START_ACTIVITY,
    activityId: activityId,
    description: description
});

export const finishActivityAction = (activityId) => ({
    type: FINISH_ACTIVITY,
    activityId: activityId
});