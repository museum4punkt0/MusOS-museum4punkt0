/**
 * Loader React component
 * 
 * @author    Maurizio Tidei
 * @copyright © 2018 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


import React from 'react';
import {connect} from "react-redux";
import LinearProgress from "@material-ui/core/LinearProgress";
import { withStyles } from '@material-ui/core/styles';
import _ from 'lodash';


/**
 * Loader is a React component representing a loading state
 *
 * @author Maurizio Tidei
 */
class Loader extends React.Component {

    render() {

        const { classes } = this.props;

        return <div className={classes.bottomBar}>
            {this.props.active ? <LinearProgress classes={{ colorPrimary: classes.colorPrimary, barColorPrimary: classes.barColorPrimary}}/> : undefined}
        </div>
    }
}

const styles = {
    root: {
        flexGrow: 1,
    },
    colorPrimary: {
        backgroundColor: '#ffffff',
    },
    barColorPrimary: {
        backgroundColor: '#0efbd0',
    },
    bottomBar: {
        width: "100%",
        position: "fixed",
        bottom: 0
    }
};

const mapStateToProps = state => {
    const activityCount = _.size(state.activity.activities);
    return {
        active: activityCount > 0
    }
}

export default connect(mapStateToProps)(withStyles(styles)(Loader));
