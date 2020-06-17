/**
 * CBox redux constants
 * 
 * @author    Jens Gruschel, Maurizio Tidei
 * @copyright © 2019 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


// redux action IDs
export const INIT_BOX                       = 'INIT_BOX';
export const HALT_BOX                       = 'HALT_BOX';
export const SET_MEDIA_URL                  = 'SET_MEDIA_URL';
export const SET_BOX_PROPERTIES             = 'SET_BOX_PROPERTIES';
export const SET_BOX_CONTENT                = 'SET_BOX_CONTENT';
export const SET_BOX_SCREENSAVER            = 'SET_BOX_SCREENSAVER';
export const SHOW_SCREENSAVER               = 'SHOW_SCREENSAVER';
export const RESET_IDLE_TIMER               = 'RESET_IDLE_TIMER';
export const SHOW_CHAT_MESSAGE              = 'SHOW_CHAT_MESSAGE';
export const SHOW_CHAT_INTERACTION          = 'SHOW_CHAT_INTERACTION';
export const SHOW_CHAT_ANSWER               = 'SHOW_CHAT_ANSWER';
export const CLEAR_CHAT                     = 'CLEAR_CHAT';
export const SHOW_CHAT                      = 'SHOW_CHAT';
export const SHOW_NOTIFICATION              = 'SHOW_NOTIFICATION';
export const PAUSE_PLAYBACK_ACTION          = 'PAUSE_PLAYBACK_ACTION';
export const RESUME_PLAYBACK_ACTION         = 'RESUME_PLAYBACK_ACTION';
export const STOP_PLAYBACK_ACTION           = 'STOP_PLAYBACK_ACTION';
export const SET_PLAYBACK_VOLUME_ACTION     = 'SET_PLAYBACK_VOLUME_ACTION';
export const SET_BOX_MENU_ACTION            = 'SET_BOX_MENU_ACTION';
export const SET_BOX_MENU_FLAGS_ACTION      = 'SET_BOX_MENU_FLAGS_ACTION';
export const SET_BOX_CONTEXT                = 'SET_BOX_CONTEXT';


// modes
export const CONTENT_MODE       = 'CONTENT';
export const CHAT_MODE          = 'CHAT';