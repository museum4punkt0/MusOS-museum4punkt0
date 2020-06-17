/**
 * types operations
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
    REST_CALL_LIST_TYPES,
    REST_SERVER_BASE_URL
} from "../config";
import {loadTypeDefinitionsSuccessAction} from "../redux/types/actions";
import {fetchJSONActivity} from "./communication";


export function loadTypeDefinitions() {

    return async (dispatch, getState) => {

        try {
            // do server communication
            const { authorization } = getState();
            const typeDefinitions = await fetchJSONActivity(dispatch, "loading types",
                REST_SERVER_BASE_URL + REST_CALL_LIST_TYPES.path, {
                    method: REST_CALL_LIST_TYPES.method,
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer " + authorization.accessToken
                    }
                }
            );

            // handle response
            console.log("object type definitions:", typeDefinitions);
            dispatch(loadTypeDefinitionsSuccessAction(typeDefinitions));
        }
        catch (error) {
            console.log("type definition error:", error);
        }
    }
}