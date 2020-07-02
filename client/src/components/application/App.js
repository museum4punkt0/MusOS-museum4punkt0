/**
 * App React component (application root)
 * 
 * @author    Maurizio Tidei, Jens Gruschel
 * @copyright © 2018 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


import React from 'react';
import {MuiThemeProvider, createMuiTheme} from '@material-ui/core/styles';
import {Provider} from 'react-redux';
import store from '../../store.js';

import '../../App.css';

import {loginBox} from '../../operations/login';
import {addSocketListener} from "../../operations/cbox";
import {REST_SERVER_BASE_URL} from "../../config";
import io from "socket.io-client"
import CBoxView from "../presentation/CBoxView";
import {extractURLParams} from "../../utils";


const themeMusos = createMuiTheme(
    {
        typography: {
            useNextVariants: true,
        },
        palette: {
            primary: {main: '#147c91'}, // #049bbf, #063446, #0a7dab, #147c91
            secondary: {main: '#1aa3bf'}, // 0dfbd0
            notification: {main: '#ff0000'}
        },
        overrides: {
            MuiNotchedOutline: {
                root: {
                    borderColor: "#949494"
                }
            }
        }
    });


/**
 * App is the root component of the application usually showing the main view
 */
class App extends React.Component {

    socket = null;

    constructor(props) {
        super(props);

        const params = extractURLParams();
        console.log("URL params", params);
        const cboxName = params["cbox"] || 'cbox';

        const screenIndex = params["screen"] || 0;
        this.initCbox(cboxName, screenIndex);
    }

    initCbox(cboxName, screenIndex) {

        console.log("cbox name", cboxName, "screen", screenIndex);
        loginBox(cboxName, screenIndex)(store.dispatch, store.getState);
        document.title = 'cbox-' + cboxName + '-' + screenIndex;

        // connect
        this.socket = io.connect(REST_SERVER_BASE_URL);

        this.socket.on('connect', () => {
            console.log("connected with " + REST_SERVER_BASE_URL);
            this.socket.emit("joinbox", {name: cboxName});
        });

        this.socket.on('connect_error', (error) => {
            console.log("error connecting to " + REST_SERVER_BASE_URL + ":", error);
        });

        this.socket.on('connect_timeout', (timeout) => {
            console.log("timeout connecting to " + REST_SERVER_BASE_URL + ":", timeout);
        });

        this.socket.on('disconnect', () => {
            console.log("disconnected from " + REST_SERVER_BASE_URL);
        });

        this.socket.on('reconnect', () => {
            // 'connect' is also fired on 'reconnect',
            // so there is nothing to do here (right now)
        });

        store.dispatch(addSocketListener(this.socket));
    }

    render() {

        const onAlive = (active, activity) => {
            if (this.socket) {
                this.socket.emit("alive", {"active": active, "activity": activity});
            }
        }
            
        return (
            <MuiThemeProvider theme={themeMusos}>
                <Provider store={store}>
                    <div>
                        <CBoxView onAlive={onAlive}/>
                    </div>
                </Provider>
            </MuiThemeProvider>
        );
    }
}

export default App;

