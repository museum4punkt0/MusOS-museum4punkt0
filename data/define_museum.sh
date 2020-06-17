#!/usr/bin/env bash

declare -a museumfiles=(

    # exhibit types
    data/types/type_inventory

    # administration types
    data/types/type_event
    data/types/type_service

    # infrastructure types
    data/types/type_beaconrange
    data/types/type_badge
    data/types/type_badgesensor

    # story telling types
    data/types/type_avatar
    data/types/type_visitortype
    data/types/type_taggedmediaautomatism
    data/types/type_textaction
    data/types/type_interactioncase
    data/types/type_interaction
    data/types/type_sceneselection
    data/types/type_story

    # museum roles and users
    data/roles/role_curator
    data/roles/role_scenography

    # misc
    data/misc/channel_allmobiles
    data/misc/stylesheet_cbox_chat_standard
)
