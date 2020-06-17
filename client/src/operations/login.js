/**
 * login operations
 * 
 * @author    Jens Gruschel
 * @copyright © 2018 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


import {loginSuccessAction} from "../redux/authorization/actions";
import {
    REST_CALL_LOGIN,
    REST_SERVER_BASE_URL
} from "../config";
import {loadTypeDefinitions} from "./types";
import {fetchJSONActivity} from "./communication";
import {refreshBox} from "./cbox";
import {initBoxAction} from "../redux/cbox/actions";


export function loginBox(cboxName, screenIndex) {

    return async (dispatch, getState) => {

        const user = "cbox";
        const password = "d5TL55llb0xRfZZMS9rUuVnA";
        const requestData = {"user": user, "password": password};

        try {
            // perform server communication
            const json = await fetchJSONActivity(dispatch, "logging in",
                REST_SERVER_BASE_URL + REST_CALL_LOGIN.path, {
                    method: REST_CALL_LOGIN.method,
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(requestData)
                }
            );

            // remember token for this session
            if (typeof(Storage) !== "undefined") {
                sessionStorage.setItem('token', json.accessToken);
            }

            // process response
            dispatch(loginSuccessAction(json.accessToken));

            // init application
            await loadTypeDefinitions()(dispatch, getState);
            dispatch(initBoxAction(cboxName, screenIndex));
            await refreshBox(cboxName)(dispatch, getState);
        }
        catch (error) {
            console.log("login error:", error);
        }
    }
}
