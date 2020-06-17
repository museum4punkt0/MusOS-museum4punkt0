/**
 * MenuFrame React component
 * 
 * @author    Jens Gruschel
 * @copyright © 2019 contexagon GmbH
 *
 * @license
 * This file is part of MusOS and is released under the GPLv3 license.
 * Please see the LICENSE.md file that should have been included
 * as part of this package.
 */


// React
import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {withStyles} from "@material-ui/core";

// Material-UI components
import Slide from '@material-ui/core/Slide';
import Collapse from '@material-ui/core/Collapse';

// 3rd party
import _ from 'lodash';

// application components
import DraggableMenuObject from "./DraggableMenuObject";

// application
import {selectTranslation} from "../../redux/configuration/selectors";
import {triggerMenuAction} from "../../operations/cbox";
import {setBoxMenuFlagsAction, setBoxContextAction} from "../../redux/cbox/actions";
import {findTaggedImage} from "../../utils";
import {patchServerUrl} from "../../config";

function getClassNames(name, level, selected) {
    if (selected) {
        return name + " menulevel-" + level + " menuselected";
    }
    else {
        return name + " menulevel-" + level;
    }
}

function getAnimationDirection(menu) {
    if (!menu || !menu.fields) return undefined;
    const animation = menu.fields.animation;
    switch (animation) {
        case "left": return animation;
        case "right": return animation;
        case "up": return animation;
        case "down": return animation;
        default: return undefined;
    }
}

function isAnimated(menu) {
    return !!getAnimationDirection(menu);
}

function getFlexJustification(position) {
    switch(position) {
        case "top-left":
        case "top-center":
        case "top-right":
            return "flex-start";

        case "bottom-left":
        case "bottom-center":
        case "bottom-right":
            return "flex-end";

        case "middle-left":
        case "middle-center":
        case "middle-right":
            return "center";

        default:
            return undefined;
    }
}

function getMenuStyle(display, position, orientation) {
    const flexDirection = orientation === "horizontal" ? "row" : "column";
    const result = {flexDirection: flexDirection};
    if (display === "above") {
        return {
            ...result,
            "position": "absolute",
            "left": ["left", "top", "bottom", "top-left", "middle-left", "bottom-left", "full"].includes(position) ? 0 : undefined,
            "right": ["right", "top", "bottom", "top-right", "middle-right", "bottom-right", "full"].includes(position) ? 0 : undefined,
            "top": ["top", "left", "right", "top-left", "top-center", "top-right", "full"].includes(position) ? 0 : undefined,
            "bottom": ["bottom", "left", "right", "bottom-left", "bottom-center", "bottom-right", "full"].includes(position) ? 0 : undefined,
        }
    }
    else if (display === "sidewards") {
        return {
            ...result,
            order: ["right", "top-right", "middle-right", "bottom-right"].includes(position) ? 1 : -1,
            alignSelf: "stretch",
            justifyContent: getFlexJustification(position),
            flexGrow: 0,
            flexShrink: 0
        }
    }
    else {
        return result;
    }
}

/**
 * Component showing a menu on a CBox
 *
 * This component holds the menu and menu flags in its own state in order
 * to animate the menu (if it changes, the old one is not replaced instantly,
 * but slided out and later replaced by the one given by the props).
 * 
 * @author Jens Gruschel
 */
class MenuFrame extends React.Component {

    state = {
        menu: undefined,
        flags: {},
        selectedIndex: undefined
    }

    componentDidUpdate(prevProps) {
        if (isAnimated(this.state.menu) && !_.isEqual(this.props.menu, prevProps.menu) && this.state.flags.visible) {
            // hide animated menu before showing new one (see handleMenuExited)
            this.setState({flags: {...this.state.flags, visible: false}});
        }
        else if (this.props.menu !== prevProps.menu || this.props.flags !== prevProps.flags) {
            // just change state (might trigger animation either in or out)
            this.setState({menu: this.props.menu, flags: this.props.flags || {}})
        }
    }

    clickItem(menuId, index, isSubMenuHeader) {

        this.setState({selectedIndex: index});
        this.props.triggerMenuAction(menuId, index, this.props.flags.context || {});
        if (!isSubMenuHeader && this.state.menu && this.state.menu.fields && this.state.menu.fields.autohide) {
            this.props.setBoxMenuFlagsAction(this.props.slot, {visible: false});
        }
    }

    clickSubject(menuId, index, subject, referencedObjects, operation) {

        switch (operation) {
            case "replace":
            case "append":
            case "insert":
                this.props.setBoxContextAction([subject], [referencedObjects], operation);
                break;
            default:
                break;
        }

        this.clickItem(menuId, index, false);
    }

    dropSubject( subject, referencedObjects, index) {
        this.props.setBoxContextAction([subject], [referencedObjects], "put", index);
    }

    handleMenuExited() {
        // no that the previous menu is gone,
        // we can show the new one
        if (this.state.menu !== this.props.menu) {
            // replace everything completly
            // (the new menu might be visible or not)
            this.setState({
                menu: this.props.menu,
                flags: this.props.flags || {},
                selectedIndex: undefined
            });
        }
        else if (this.state.flags !== this.props.flags) {
            // the same menu is still there (just hidden)
            // so just replace the flags,
            // keep the selected index
            this.setState({
                flags: this.props.flags || {}
            });
        }
    }

    render() {

        const menu = this.state.menu;
        if (!menu) return null;

        const menuId = menu.id;
        const fields = menu.fields || {};
        const { display, position, orientation } = fields;
        const style = getMenuStyle(display, position, orientation);
        const items = fields.items || [];

        if (isAnimated(menu)) {
            return <Slide in={this.state.flags.visible} direction={getAnimationDirection(menu)} onExited={() => this.handleMenuExited()}>
                {this.renderMenu(items, menuId, orientation, style)}
            </Slide>;
        }
        else if (this.state.flags.visible) {
            return this.renderMenu(items, menuId, orientation, style);
        }
        else {
            return null;
        }
    }

    renderMenu(items, menuId, orientation, style) {
        return <nav id={this.props.elementId} className="menuframe" style={style}>
            {items.map((item, index) => this.renderItem(item, 1, menuId, index, orientation, false))}
        </nav>
    }

    renderItem(item, level, menuId, index, orientation, isSubMenuHeader, selected = false) {

        switch (item.type) {
            case "submenu": return this.renderSubMenu(item, level, menuId, index);
            case "menuobjectselection": return this.renderObjectSelection(item, level, menuId, index);
            case "menubutton": return this.renderButton(item, level, menuId, index, isSubMenuHeader, selected);
            case "menuicon": return this.renderIcon(item, level, menuId, index, isSubMenuHeader, selected);
            case "menuimage": return this.renderImage(item, level, menuId, index, isSubMenuHeader, selected);
            case "menuheading": return this.renderHeading(item, level);
            case "menutext": return this.renderText(item, level);
            case "menuspace": return this.renderSpace(item, level, orientation);
            default: return undefined;
        }
    }

    renderSubMenu(item, level, menuId, index) {

        const fields = item.fields || {};
        const orientation = fields.orientation;
        const mode = fields.mode;
        const flexDirection = orientation === "horizontal" ? "row" : "column";
        const header = fields.header || [];
        const items = fields.items || [];
        const selected = this.state.selectedIndex && this.state.selectedIndex.toString().startsWith(index);

        return <div key={index}>
            <Collapse in={!selected || mode !== "replace"}>
                {header.length > 0 && this.renderItem(header[0], level, menuId, index, orientation, true, selected)}
            </Collapse>
            <Collapse in={selected || mode === "static"}>
                <div className="submenu" style={{flexDirection: flexDirection}}>
                    {items.map((item, i) => this.renderItem(item, level + 1, menuId, index + ";" + i, orientation, false))}
                </div>
            </Collapse>
        </div>;
    }

    renderObjectSelection(item, level, menuId, index) {

        const fields = item.fields || {};
        const orientation = fields.orientation;
        const flexDirection = orientation === "horizontal" ? "row" : "column";
        const items = fields.items || [];
        const tags = fields.imagetags || [];
        const operation = fields.operation;
        const selected = this.state.selectedIndex && this.state.selectedIndex.toString().startsWith(index);

        return <div key={index} className="menuobjectselection" style={{flexDirection: flexDirection}}>
            {items.map((item, i) => this.renderReferencedObject(item, tags, level + 1, menuId, index + ";" + i, operation, selected))}
        </div>;
    }

    renderReferencedObject(id, tags, level, menuId, index, operation, selected = false) {

        const item = this.props.referencedObjects[id];
        if (!item) return null;
        const itemText = this.props.translate(item.title);
        const itemImage = findTaggedImage(item, this.props.referencedObjects, tags);
        const itemImageUrl = patchServerUrl((itemImage && itemImage.fields && itemImage.fields.url) || item.imageurl);
        const isSubject = !!this.props.subjects.find(subject => subject && subject.id === id);
        const classNames = getClassNames("menuobject", level, selected) + (isSubject ? " subject" : "");

        if (operation === "draganddrop") {
            return <div key={id} id={"menuobject-" + id} className={classNames}>
                <DraggableMenuObject
                    id={id}
                    imageUrl={itemImageUrl}
                    labelText={itemText}
                    onDrop={index => {
                        this.dropSubject(item, [itemImage], index);
                    }}
                />
            </div>;
        }
        else {
            return <div key={id} id={"menuobject-" + id} className={classNames}
                onClick={() => this.clickSubject(menuId, index, item, [itemImage], operation)}
            >
                {itemImageUrl && <img src={itemImageUrl} alt={itemText} />}
                <label>{itemText}</label>
            </div>;
        }
    }

    renderButton(item, level, menuId, index, isSubMenuHeader, selected = false) {

        const itemText = this.props.translate(item.fields.text);
        const itemIconUrl = patchServerUrl(item.fields.iconurl);

        return <div key={"menubutton-" + itemText} className={getClassNames("menubutton", level, selected)}
            onClick={() => this.clickItem(menuId, index, isSubMenuHeader)}
        >
            {itemIconUrl && <img src={itemIconUrl} alt={itemText} />}
            <label>{itemText}</label>
        </div>;
    }

    renderIcon(item, level, menuId, index, isSubMenuHeader, selected = false) {

        const itemIconUrl = patchServerUrl(item.fields.iconurl);

        return <div key={"menuicon-" + itemIconUrl} className={getClassNames("menuicon", level, selected)}
            onClick={() => this.clickItem(menuId, index, isSubMenuHeader)}
        >
            <img src={itemIconUrl} alt="icon" />
        </div>;
    }

    renderImage(item, level, menuId, index, isSubMenuHeader, selected = false) {

        const itemImageUrl = patchServerUrl(item.fields.imageurl);

        return <div key={"menuimage-" + itemImageUrl} className={getClassNames("menuimage", level, selected)}
            onClick={() => this.clickItem(menuId, index, isSubMenuHeader)}
        >
            <img src={itemImageUrl} alt="" />
        </div>;
    }

    renderHeading(item, level) {

        const itemText = this.props.translate(item.fields.text);

        return <div key={"menuheading-" + itemText} className={getClassNames("menuheading", level, false)}>
            <h1>{itemText}</h1>
        </div>;
    }

    renderText(item, level) {

        const itemText = this.props.translate(item.fields.text);

        return <div key={"menutext-" + itemText} className={getClassNames("menutext", level, false)}>
            <p>{itemText}</p>
        </div>;
    }

    renderSpace(item, level, orientation) {

        const dimension = orientation === "horizontal" ? "width" : "height";
        const distance = item.fields.distance;
        const suffix = item.fields.distance__suffix;
        const style = {[dimension]: distance + suffix};

        return <div key={"menuspace-" + distance} className={getClassNames("menuspace", level, false)} style={style} />
    }
}

MenuFrame.propTypes = {
    slot: PropTypes.string.isRequired,
    elementId: PropTypes.string.isRequired,
    stylesheet: PropTypes.string,
    menu: PropTypes.object,
    flags: PropTypes.object
};

const styles = theme => ({
});

const mapStateToProps = state => {
    return {
        subjects: state.cbox.context.subjects || [],
        translate: (value) => selectTranslation(state.configuration, value, state.cbox.language)
    };
};

export default connect(
    mapStateToProps, {
        triggerMenuAction,
        setBoxMenuFlagsAction,
        setBoxContextAction
    }
)(withStyles(styles)(MenuFrame));