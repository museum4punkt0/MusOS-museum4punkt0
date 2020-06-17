#!/usr/bin/env bash

declare -a standardfiles=(

    # system types
    data/types/type_access
    data/types/type_type
    data/types/type_mediaitem
    data/types/type_role
    data/types/type_user
    data/types/type_cboxshortcut
    data/types/type_textparameter
    data/types/type_configuration
    data/types/type_usersettings
    data/types/type_htmltemplate

    # administration types
    data/types/type_reminder
    data/types/type_contact

    # infrastructure types
    data/types/type_cbox
    data/types/type_channel
    data/types/type_simpletrigger

    # content types
    data/types/type_stylesheet
    data/types/type_textslide
    data/types/type_htmlcontent
    data/types/type_objectinfopanel
    data/types/type_menubutton
    data/types/type_menutext
    data/types/type_menuheading
    data/types/type_menuicon
    data/types/type_menuimage
    data/types/type_menuspace
    data/types/type_submenu
    data/types/type_menuobjectselection
    data/types/type_menuframe

    # action types
    data/types/type_stateproperty
    data/types/type_controlaction
    data/types/type_mediaaction
    data/types/type_contentaction
    data/types/type_sceneaction
    data/types/type_notificationaction
    data/types/type_menuaction
    data/types/type_stateaction
    data/types/type_exactvaluecondition
    data/types/type_rangecondition
    data/types/type_randomcondition
    data/types/type_timecondition
    data/types/type_conditionalaction
    data/types/type_case
    data/types/type_caseaction
    data/types/type_scene

    # standard roles and users
    data/roles/role_system
    data/roles/role_developer
    data/roles/role_any
    data/roles/role_admin
    data/roles/role_standard
    data/roles/role_supervisor
    data/roles/role_cbox
    data/roles/role_guest
    data/roles/role_designer
    data/roles/role_office
    data/users/user_system
    data/users/user_admin
    data/users/user_cbox

    # misc
    data/misc/configuration_active
    data/misc/channel_broadcast
    data/misc/channel_allboxes
    data/misc/stylesheet_standard_center_white
    data/misc/stylesheet_standard_center_black

    # test data
    data/test/textslide_test
    data/test/cbox_test
)
