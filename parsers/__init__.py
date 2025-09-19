import os
from .generic import GenericParser
from .achievement import AchievementParser
from .activity import ActivityParser
from .activityrequest import ActivityrequestParser
from .activityrequestsettingsdata import ActivityrequestsettingsdataParser
from .aihitreactions import AihitreactionsParser
from .aim_assist_parameters import AimAssistParametersParser
from .animupdaterateparams import AnimupdaterateparamsParser
from .attribute import AttributeParser
from .audio_event import AudioEventParser
from .audioprovider import AudioproviderParser
from .base import BaseParser
from .camera_mode import CameraModeParser
from .camera_shake import CameraShakeParser
from .camera_transition import CameraTransitionParser
from .capital import CapitalParser
from .character import CharacterParser
from .generic import GenericParser
from .inv_name_part import InvNamePartParser
from .inventory import InventoryParser
from .light_beam import LightBeamParser
from .light_projectile import LightProjectileParser
from .loot_config import LootConfigParser
from .luck_category import LuckCategoryParser
from .managed_actor import ManagedActorParser
from .mantle import MantleParser
from .manufacturer import ManufacturerParser
from .quest import QuestParser
from .quests import QuestsParser

ALL_PARSERS = [
    AchievementParser,
    ActivityParser,
    ActivityrequestParser,
    ActivityrequestsettingsdataParser,
    AihitreactionsParser,
    AimAssistParametersParser,
    AnimupdaterateparamsParser,
    AttributeParser,
    AudioEventParser,
    AudioproviderParser,
    CameraModeParser,
    CameraShakeParser,
    CameraTransitionParser,
    CapitalParser,
    CharacterParser,
    InvNamePartParser,
    InventoryParser,
    LightBeamParser,
    LightProjectileParser,
    LootConfigParser,
    LuckCategoryParser,
    ManagedActorParser,
    MantleParser,
    ManufacturerParser,
    QuestParser,
    QuestsParser,
    GenericParser,
]

def get_parser_for(filepath):
    fname = os.path.basename(filepath)
    with open(filepath, 'rb') as f:
        raw = f.read()
    for P in ALL_PARSERS:
        try:
            if P.can_parse(fname, raw):
                return P()
        except Exception:
            pass
    return GenericParser()

def get_parser(filepath):
    return get_parser_for(filepath)