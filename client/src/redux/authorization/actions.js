/**
 * authorization redux actions
 * 
 * @author    Jens Gruschel
 * @copyright © 2018 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


import {LOGIN_SUCCESS} from "./consts";
import {LOGOUT} from "../authorization/consts"; // TODO: how to handle global actions?


export const loginSuccessAction = (accessToken) => ({
    type: LOGIN_SUCCESS,
    accessToken: accessToken
});

export const logoutAction = () => ({
    type: LOGOUT
});