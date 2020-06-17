/**
 * communication utilities
 * 
 * @author    Jens Gruschel
 * @copyright © 2018 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


import {finishActivityAction, startActivityAction} from "../redux/activity/actions";
import {generateActivityId} from "../utils";
import {sleep} from "../utils";


/**
 * asynchronously fetch JSON data from server and handle errors (such as 404 or invalid JSON format)
 */
export async function fetchJSON(path, options) {

    // perform server communication
    const logging = true; // TODO
    if (logging) console.log("fetch:", path, options);
    const response = await fetch(path, options);
    if (logging) console.log("response:", response);
    if (response.status >= 400) {
        let text = "";
        try {
            // get error message text from JSON error object if possible
            // (without cloning the response it is not possible to get the response text afterwards,
            // because the "body has already been consumed")
            const data = await response.clone().json();
            text = data.message || await response.text();
        }
        catch (error) {
            // no valid JSON error object
            text = await response.text();
            console.log("server returned non-json answer: ", text);
        }
        throw new Error("error " + response.status + ": " + response.statusText + " (" + text + ")");
    }

    // parse response
    try {
        const data = await response.json();
        return data;
    }
    catch (error) {
        throw new Error("invalid server response");
    }
}

/**
 * asynchronously fetch JSON data from server and handle errors (such as 404 or invalid JSON format),
 * while opening and closing an activity with a given description
 */
export async function fetchJSONActivity(dispatch, description, path, options) {

    // indicate start of activity
    const activityId = generateActivityId();
    dispatch(startActivityAction(activityId, description));

    // wait a bit to simulate slow connections
    const simulateSlowConnection = false;
    if (simulateSlowConnection) {
        await sleep(1000);
    }

    try {
        // perform server communication and parse response
        return await fetchJSON(path, options)
    }
    finally {
        // don't forget to indicate end of activity
        dispatch(finishActivityAction(activityId));
    }
}