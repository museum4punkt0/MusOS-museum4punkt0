/**
 * authorization redux constants
 * 
 * @author    Jens Gruschel
 * @copyright © 2018 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


// redux action IDs
export const LOGIN_SUCCESS                  = 'LOGIN_SUCCESS';
export const LOGOUT                         = 'LOGOUT';


// accessibility levels
export const ACCESS_UNDEFINED   = 0;
export const ACCESS_HIDDEN      = 1;
export const ACCESS_READONLY    = 2;
export const ACCESS_WRITABLE    = 3;


/**
 * get level (1, 2, 3) for accessibility name ("hidden", "readonly", "writable")
 * @param {string} accessibility    accessibility name
 * @returns {number}                level 0 ("hidden"), 1 ("readonly") or 2 ("writable")
 * @author Jens Gruschel
 */
export function getAccessibilityLevel(accessibility) {
    if (accessibility === "hidden") return ACCESS_HIDDEN;
    if (accessibility === "readonly") return ACCESS_READONLY;
    return ACCESS_WRITABLE; // default is writable (especially if not specified at all)
}
