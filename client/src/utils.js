/**
 * functions for date/time formatting etc.
 * 
 * @author    Maurizio Tidei, Jens Gruschel
 * @copyright © 2018 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */

 
// 3rd party
import _ from 'lodash';


const absoluteUrlPattern = new RegExp('^([A-Za-z]+://|//)');

export function isAbsoluteUrl(url) {
    return absoluteUrlPattern.test(url);
}

export function getDateForFileName(date) {
    const yyyy = date.getFullYear().toString();
    const MM = pad(date.getMonth() + 1, 2);
    const dd = pad(date.getDate(), 2);
    const hh = pad(date.getHours(), 2);
    const mm = pad(date.getMinutes(), 2)
    const ss = pad(date.getSeconds(), 2)

    return yyyy + MM + dd + "_" + hh + mm + ss;
};

function pad(number, length, char = '0') {
    let str = '' + number;
    while (str.length < length) {
        str = char + str;
    }
    return str;
}

export function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

export function generateActivityId() {
    return Math.floor((Math.random() * 1000000000000000));
}

export function generateTemporaryObjectId(typeId) {
    return typeId + ".temp." + Math.floor((Math.random() * 1000000000000000));
}

export function toLocalISODateString(date) {
    if (!date) return "";
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    return pad(year, 4) + '-' + pad(month, 2) + '-' + pad(day, 2);
}

export function toLocalISOTimeString(date, withSeconds = true) {
    if (!date) return "";
    const hour = date.getHours();
    const minute = date.getMinutes();
    if (!withSeconds) return pad(hour, 2) + ':' + pad(minute, 2);
    const second = date.getSeconds();
    return pad(hour, 2) + ':' + pad(minute, 2) + ':' + pad(second, 2);
}

export function toTimeOnlyDate(timeString) {
    if (!timeString || timeString.length === 0) return null;
    return new Date('1970-01-01T' + timeString);
}

export function toUserFriendlyDateTimeString(date) {
    if (!date) return "";
    let today = new Date();
    today.setHours(0, 0, 0, 0);
    let dateDay = new Date(date.valueOf());
    dateDay.setHours(0, 0, 0, 0);
    const diff = Math.round((today - dateDay) / 86400000);
    if (diff === 0) {
        return "heute um " + date.toLocaleTimeString();
    }
    else if (diff === 1) {
        return "gestern um " + date.toLocaleTimeString();
    }
    else {
        return "am " + date.toLocaleDateString() + " um " + date.toLocaleTimeString();
    }
}

export function toUserFriendlySecondsString(seconds) {
    const secs = Math.round(seconds);
    if (secs < 60) {
        return '0:' + pad(secs, 2);
    }
    else if (secs < 3600) {
        return pad(Math.floor(secs / 60), 2) + ':' + pad(secs % 60, 2);
    }
    else if (secs < 86400) {
        return pad(Math.floor(secs / 3600), 2) + ':' + pad(Math.floor(secs / 60) % 60, 2) + ':' + pad(secs % 60, 2);
    }
    else if (secs < 2 * 86400) {
        return "1 Tag " + pad(Math.floor(secs / 3600), 2) + ':' + pad(Math.floor(secs / 60) % 60, 2) + ':' + pad(secs % 60, 2);
    }
    else {
        return Math.floor(secs / 86400) + " Tage " + pad(Math.floor(secs / 3600) % 24, 2) + ':' + pad(Math.floor(secs / 60) % 60, 2) + ':' + pad(secs % 60, 2);
    }
}

export function getFileExtension(url) {

    const fileExtension = url !== undefined ? url.substr(url.lastIndexOf(".") + 1).toLowerCase() : "";
    return fileExtension;
}

export function getMediaType(url) {

    const fileExtension = getFileExtension(url);
    switch(fileExtension) {

        case "mp4":
        case "webm":
        case "ogg":
            return "video";

        case "mp3":
        case "wav":
        case "m4a":
            return "audio";

        case "pdf":
            return "pdf";

        case "png":
        case "gif":
        case "jpg":
        case "jpeg":
        case "jpe":
        case "jfif":
        case "jif":
        case "jfi":
        case "svg":
        case "webp":
            return "image";

        default:
            return "other";
    }
}

export function getCountryCodeForLanguage(code) {
    if (code === 'en') return 'gb';
    else return code;
}

export function parseBSON(value, defaultValue, name) {
    // parse strings because MongoDBs BSON does not allow "$" or "." in keys as JSON does
    if (value === undefined) return undefined;
    try {
        return JSON.parse(value);
    }
    catch(error) {
        console.log("could not parse BSON for", name, "because of", value);
        return defaultValue;
    }
}

export function extractURLParams() {

    let result = {};
    const text = window.location.search.slice(1); // remove "?" at the very beginning
    const params = text.split("&");

    for (const param of params) {
        const pos = param.indexOf("=");
        if (pos > 0) {
            const name = param.slice(0, pos);
            const value = param.slice(pos + 1);
            result[name] = value;
        }
        else
        {
            result[param] = null;
        }
    }

    return result;
}

/**
 * Uses canvas.measureText to compute and return the width of the given text of given font in pixels.
 *
 * @param {String} text The text to be rendered.
 * @param {String} font The css font descriptor that text is to be rendered with (e.g. "bold 14px verdana").
 *
 * @see https://stackoverflow.com/questions/118241/calculate-text-width-with-javascript/21015393#21015393
 */
export function getTextWidth(text, font) {
    // re-use canvas object for better performance
    let canvas = getTextWidth.canvas || (getTextWidth.canvas = document.createElement("canvas"));
    let context = canvas.getContext("2d");
    context.font = font;
    let metrics = context.measureText(text);
    return metrics.width;
}

export function findTaggedImage(item, referencedObjects, tags) {

    if (!tags || tags.length === 0) return null;

    const mediaItemIds = item.fields.medialist; // TODO: does not work for media item fields with other name (also see action_engine.py)
    for (const id of mediaItemIds) {
        const mediaItem = referencedObjects[id];
        if (mediaItem) {
            const itemTags = mediaItem.tags;
            if (_.difference(tags, itemTags).length === 0) {
                // all tags are in itemTags
                return mediaItem;
            }
        }
    }
    return null;
}
