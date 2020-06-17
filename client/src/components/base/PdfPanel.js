/**
 * PdfPanel React component
 * 
 * @author    Jens Gruschel
 * @copyright © 2020 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


// React
import React from 'react';

// Material-UI
import {withStyles} from '@material-ui/core/styles';

// 3rd party
import { Document, Page } from 'react-pdf/dist/entry.webpack'; // right now webpack is used


/**
 * PdfPanel sizes and renders a PDF document
 *
 * @author Jens Gruschel
 */
export class PdfPanel extends React.Component {

    constructor(props) {
        super(props);
        this.state = {width: null, height: null};
    }
    
    componentDidMount () {
        this.updateDimensions();
        this.timer = setInterval(() => {this.updateDimensions()}, 500);
        // window.addEventListener("resize", _.throttle(this.updateDimensions, 500)); // does not fire on animations
    }
    
    componentWillUnmount () {
        clearInterval(this.timer);
        // window.removeEventListener("resize", _.throttle(this.updateDimensions, 500)); // does not fire on animations
    }
    
    updateDimensions = () => {
        if (this.wrapper) {
            const rect = this.wrapper.getBoundingClientRect();
            if (this.width !== rect.width || this.height !== rect.height) {
                this.setState({
                    width: rect.width,
                    height: rect.height
                });
            }
        }
    }
    
    render() {

        const {classes} = this.props;

        return <div className={classes.wrapper} ref={ref => this.wrapper = ref}>
            <Document
                file={this.props.file}
                onLoadError={console.error}
            >
                <Page pageNumber={1} width={this.state.width} />
            </Document>
        </div>;
    }
}

const styles = theme => ({
    wrapper: {
        position: "absolute",
        left: 0,
        right: 0,
        top: 0,
        bottom: 0,
        "& .react-pdf__Document": {
            display: "flex",
            justifyContent: "center"
        }    
    }
});

export default withStyles(styles)(PdfPanel);