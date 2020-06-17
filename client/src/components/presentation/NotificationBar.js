/**
 * NotificationBar React component
 * 
 * @author    Jens Gruschel
 * @copyright © 2019 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


import React from 'react';
import {withStyles} from "@material-ui/core";


/**
 * NotificationBar
 *
 * @author Jens Gruschel
 */
class NotificationBar extends React.Component {

    render() {

        const {classes} = this.props;

        if (this.props.text) {
            return <div className={classes.notificationBar}><p className={classes.notificationText}>{this.props.text}</p></div>;
        }
        else {
            return null;
        }
    }
}

const styles = theme => ({
    notificationBar: {
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        backgroundColor: "rgba(0,0,0,0.5)"
    },
    notificationText: {
        width: "100%",
        color: "#fff",
        fontSize: 40,
        textAlign: "center"
    }
});

export default withStyles(styles)(NotificationBar);