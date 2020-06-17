/**
 * server configuration
 * 
 * @author    Maurizio Tidei, Jens Gruschel
 * @copyright © 2018 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


import {isAbsoluteUrl} from "./utils";


export const REST_SERVER_BASE_URL = getServerURL(window.location.host);

export const REST_CALL_LOGIN = {method: 'POST', path: '/login'};
export const REST_CALL_LIST_TYPES = {method: 'GET', path: '/typelist'};
export const REST_CALL_REFRESH_BOX = {method: 'GET', path: '/box/<cbox>/refresh'};
export const REST_CALL_ANSWER_INTERACTION = {method: 'POST', path: '/interaction/<scene_id>/<index>/<answer>?boxname=<cbox>'};
export const REST_CALL_MENU_ACTION = {method: 'POST', path: '/menuaction/<menu_id>/<index>?boxname=<cbox>'};
export const REST_CALL_SHORTCUT_ACTION = {method: 'POST', path: '/shortcutaction/<cbox_name>/<index>'};


export function patchServerUrl(url) {
    if (!url) return url;
    if (isAbsoluteUrl(url)) return url;
    else if (url.startsWith("/")) return REST_SERVER_BASE_URL + url;
    else return REST_SERVER_BASE_URL + "/" + url;
}

/**
 * get server URL either for development or for production (depending on host port)
 * @author Jens Gruschel
*/
function getServerURL(host) {
    const DEV_NODE_SERVER_PORT = ":3000";
    const DEV_FLASK_SERVER_PORT = ":4000";
    if (host.endsWith(DEV_NODE_SERVER_PORT)) {
        // use Flask server port 4000 if Node server port 3000 is used (for development)
        return 'http://' + host.slice(0, -DEV_NODE_SERVER_PORT.length) + DEV_FLASK_SERVER_PORT;
    }
    else {
        // otherwise use no special server, but just the one used for this application (for production)
        return '';
    }
}


