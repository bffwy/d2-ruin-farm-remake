# -*- coding: utf-8 -*-

import os
import sys


# parent_dir_name = os.path.dirname(os.path.realpath(__file__))
# print(parent_dir_name)
# sys.path.append(parent_dir_name)
# sys.path.append(os.path.dirname(parent_dir_name))


import json
import requests
import fnmatch
from pathlib import Path
from utils import get_real_path

# from utils import Singleton


class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance


BASE_URL = "https://www.bungie.net"


component_path = {
    "DestinyNodeStepSummaryDefinition": "/common/destiny2_content/json/zh-chs/DestinyNodeStepSummaryDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyArtDyeChannelDefinition": "/common/destiny2_content/json/zh-chs/DestinyArtDyeChannelDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyArtDyeReferenceDefinition": "/common/destiny2_content/json/zh-chs/DestinyArtDyeReferenceDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyPlaceDefinition": "/common/destiny2_content/json/zh-chs/DestinyPlaceDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyActivityDefinition": "/common/destiny2_content/json/zh-chs/DestinyActivityDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyActivityTypeDefinition": "/common/destiny2_content/json/zh-chs/DestinyActivityTypeDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyClassDefinition": "/common/destiny2_content/json/zh-chs/DestinyClassDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyGenderDefinition": "/common/destiny2_content/json/zh-chs/DestinyGenderDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyInventoryBucketDefinition": "/common/destiny2_content/json/zh-chs/DestinyInventoryBucketDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyRaceDefinition": "/common/destiny2_content/json/zh-chs/DestinyRaceDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyTalentGridDefinition": "/common/destiny2_content/json/zh-chs/DestinyTalentGridDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyUnlockDefinition": "/common/destiny2_content/json/zh-chs/DestinyUnlockDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyStatGroupDefinition": "/common/destiny2_content/json/zh-chs/DestinyStatGroupDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyProgressionMappingDefinition": "/common/destiny2_content/json/zh-chs/DestinyProgressionMappingDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyFactionDefinition": "/common/destiny2_content/json/zh-chs/DestinyFactionDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyVendorGroupDefinition": "/common/destiny2_content/json/zh-chs/DestinyVendorGroupDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyRewardSourceDefinition": "/common/destiny2_content/json/zh-chs/DestinyRewardSourceDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyUnlockValueDefinition": "/common/destiny2_content/json/zh-chs/DestinyUnlockValueDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyRewardMappingDefinition": "/common/destiny2_content/json/zh-chs/DestinyRewardMappingDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyRewardSheetDefinition": "/common/destiny2_content/json/zh-chs/DestinyRewardSheetDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyItemCategoryDefinition": "/common/destiny2_content/json/zh-chs/DestinyItemCategoryDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyDamageTypeDefinition": "/common/destiny2_content/json/zh-chs/DestinyDamageTypeDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyActivityModeDefinition": "/common/destiny2_content/json/zh-chs/DestinyActivityModeDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyMedalTierDefinition": "/common/destiny2_content/json/zh-chs/DestinyMedalTierDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyAchievementDefinition": "/common/destiny2_content/json/zh-chs/DestinyAchievementDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyActivityGraphDefinition": "/common/destiny2_content/json/zh-chs/DestinyActivityGraphDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyActivityInteractableDefinition": "/common/destiny2_content/json/zh-chs/DestinyActivityInteractableDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyBondDefinition": "/common/destiny2_content/json/zh-chs/DestinyBondDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyCharacterCustomizationCategoryDefinition": "/common/destiny2_content/json/zh-chs/DestinyCharacterCustomizationCategoryDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyCharacterCustomizationOptionDefinition": "/common/destiny2_content/json/zh-chs/DestinyCharacterCustomizationOptionDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyCollectibleDefinition": "/common/destiny2_content/json/zh-chs/DestinyCollectibleDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyDestinationDefinition": "/common/destiny2_content/json/zh-chs/DestinyDestinationDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyEntitlementOfferDefinition": "/common/destiny2_content/json/zh-chs/DestinyEntitlementOfferDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyEquipmentSlotDefinition": "/common/destiny2_content/json/zh-chs/DestinyEquipmentSlotDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyEventCardDefinition": "/common/destiny2_content/json/zh-chs/DestinyEventCardDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyFireteamFinderActivityGraphDefinition": "/common/destiny2_content/json/zh-chs/DestinyFireteamFinderActivityGraphDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyFireteamFinderActivitySetDefinition": "/common/destiny2_content/json/zh-chs/DestinyFireteamFinderActivitySetDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyFireteamFinderLabelDefinition": "/common/destiny2_content/json/zh-chs/DestinyFireteamFinderLabelDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyFireteamFinderLabelGroupDefinition": "/common/destiny2_content/json/zh-chs/DestinyFireteamFinderLabelGroupDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyFireteamFinderOptionDefinition": "/common/destiny2_content/json/zh-chs/DestinyFireteamFinderOptionDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyFireteamFinderOptionGroupDefinition": "/common/destiny2_content/json/zh-chs/DestinyFireteamFinderOptionGroupDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyStatDefinition": "/common/destiny2_content/json/zh-chs/DestinyStatDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyInventoryItemDefinition": "/common/destiny2_content/json/zh-chs/DestinyInventoryItemDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyInventoryItemLiteDefinition": "/common/destiny2_content/json/zh-chs/DestinyInventoryItemLiteDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyItemTierTypeDefinition": "/common/destiny2_content/json/zh-chs/DestinyItemTierTypeDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyLoadoutColorDefinition": "/common/destiny2_content/json/zh-chs/DestinyLoadoutColorDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyLoadoutIconDefinition": "/common/destiny2_content/json/zh-chs/DestinyLoadoutIconDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyLoadoutNameDefinition": "/common/destiny2_content/json/zh-chs/DestinyLoadoutNameDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyLocationDefinition": "/common/destiny2_content/json/zh-chs/DestinyLocationDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyLoreDefinition": "/common/destiny2_content/json/zh-chs/DestinyLoreDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyMaterialRequirementSetDefinition": "/common/destiny2_content/json/zh-chs/DestinyMaterialRequirementSetDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyMetricDefinition": "/common/destiny2_content/json/zh-chs/DestinyMetricDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyObjectiveDefinition": "/common/destiny2_content/json/zh-chs/DestinyObjectiveDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinySandboxPerkDefinition": "/common/destiny2_content/json/zh-chs/DestinySandboxPerkDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyPlatformBucketMappingDefinition": "/common/destiny2_content/json/zh-chs/DestinyPlatformBucketMappingDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyPlugSetDefinition": "/common/destiny2_content/json/zh-chs/DestinyPlugSetDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyPowerCapDefinition": "/common/destiny2_content/json/zh-chs/DestinyPowerCapDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyPresentationNodeDefinition": "/common/destiny2_content/json/zh-chs/DestinyPresentationNodeDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyProgressionDefinition": "/common/destiny2_content/json/zh-chs/DestinyProgressionDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyProgressionLevelRequirementDefinition": "/common/destiny2_content/json/zh-chs/DestinyProgressionLevelRequirementDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyRecordDefinition": "/common/destiny2_content/json/zh-chs/DestinyRecordDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyRewardAdjusterPointerDefinition": "/common/destiny2_content/json/zh-chs/DestinyRewardAdjusterPointerDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyRewardAdjusterProgressionMapDefinition": "/common/destiny2_content/json/zh-chs/DestinyRewardAdjusterProgressionMapDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyRewardItemListDefinition": "/common/destiny2_content/json/zh-chs/DestinyRewardItemListDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinySackRewardItemListDefinition": "/common/destiny2_content/json/zh-chs/DestinySackRewardItemListDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinySandboxPatternDefinition": "/common/destiny2_content/json/zh-chs/DestinySandboxPatternDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinySeasonDefinition": "/common/destiny2_content/json/zh-chs/DestinySeasonDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinySeasonPassDefinition": "/common/destiny2_content/json/zh-chs/DestinySeasonPassDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinySocialCommendationDefinition": "/common/destiny2_content/json/zh-chs/DestinySocialCommendationDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinySocketCategoryDefinition": "/common/destiny2_content/json/zh-chs/DestinySocketCategoryDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinySocketTypeDefinition": "/common/destiny2_content/json/zh-chs/DestinySocketTypeDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyTraitDefinition": "/common/destiny2_content/json/zh-chs/DestinyTraitDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyUnlockCountMappingDefinition": "/common/destiny2_content/json/zh-chs/DestinyUnlockCountMappingDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyUnlockEventDefinition": "/common/destiny2_content/json/zh-chs/DestinyUnlockEventDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyUnlockExpressionMappingDefinition": "/common/destiny2_content/json/zh-chs/DestinyUnlockExpressionMappingDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyVendorDefinition": "/common/destiny2_content/json/zh-chs/DestinyVendorDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyMilestoneDefinition": "/common/destiny2_content/json/zh-chs/DestinyMilestoneDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyActivityModifierDefinition": "/common/destiny2_content/json/zh-chs/DestinyActivityModifierDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyReportReasonCategoryDefinition": "/common/destiny2_content/json/zh-chs/DestinyReportReasonCategoryDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyArtifactDefinition": "/common/destiny2_content/json/zh-chs/DestinyArtifactDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyBreakerTypeDefinition": "/common/destiny2_content/json/zh-chs/DestinyBreakerTypeDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyChecklistDefinition": "/common/destiny2_content/json/zh-chs/DestinyChecklistDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyEnergyTypeDefinition": "/common/destiny2_content/json/zh-chs/DestinyEnergyTypeDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinySocialCommendationNodeDefinition": "/common/destiny2_content/json/zh-chs/DestinySocialCommendationNodeDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyGuardianRankDefinition": "/common/destiny2_content/json/zh-chs/DestinyGuardianRankDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyGuardianRankConstantsDefinition": "/common/destiny2_content/json/zh-chs/DestinyGuardianRankConstantsDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyLoadoutConstantsDefinition": "/common/destiny2_content/json/zh-chs/DestinyLoadoutConstantsDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyFireteamFinderConstantsDefinition": "/common/destiny2_content/json/zh-chs/DestinyFireteamFinderConstantsDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
}
component_path_en = {
    "DestinyNodeStepSummaryDefinition": "/common/destiny2_content/json/en/DestinyNodeStepSummaryDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyArtDyeChannelDefinition": "/common/destiny2_content/json/en/DestinyArtDyeChannelDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyArtDyeReferenceDefinition": "/common/destiny2_content/json/en/DestinyArtDyeReferenceDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyPlaceDefinition": "/common/destiny2_content/json/en/DestinyPlaceDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyActivityDefinition": "/common/destiny2_content/json/en/DestinyActivityDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyActivityTypeDefinition": "/common/destiny2_content/json/en/DestinyActivityTypeDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyClassDefinition": "/common/destiny2_content/json/en/DestinyClassDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyGenderDefinition": "/common/destiny2_content/json/en/DestinyGenderDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyInventoryBucketDefinition": "/common/destiny2_content/json/en/DestinyInventoryBucketDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyRaceDefinition": "/common/destiny2_content/json/en/DestinyRaceDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyTalentGridDefinition": "/common/destiny2_content/json/en/DestinyTalentGridDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyUnlockDefinition": "/common/destiny2_content/json/en/DestinyUnlockDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyStatGroupDefinition": "/common/destiny2_content/json/en/DestinyStatGroupDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyProgressionMappingDefinition": "/common/destiny2_content/json/en/DestinyProgressionMappingDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyFactionDefinition": "/common/destiny2_content/json/en/DestinyFactionDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyVendorGroupDefinition": "/common/destiny2_content/json/en/DestinyVendorGroupDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyRewardSourceDefinition": "/common/destiny2_content/json/en/DestinyRewardSourceDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyUnlockValueDefinition": "/common/destiny2_content/json/en/DestinyUnlockValueDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyRewardMappingDefinition": "/common/destiny2_content/json/en/DestinyRewardMappingDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyRewardSheetDefinition": "/common/destiny2_content/json/en/DestinyRewardSheetDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyItemCategoryDefinition": "/common/destiny2_content/json/en/DestinyItemCategoryDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyDamageTypeDefinition": "/common/destiny2_content/json/en/DestinyDamageTypeDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyActivityModeDefinition": "/common/destiny2_content/json/en/DestinyActivityModeDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyMedalTierDefinition": "/common/destiny2_content/json/en/DestinyMedalTierDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyAchievementDefinition": "/common/destiny2_content/json/en/DestinyAchievementDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyActivityGraphDefinition": "/common/destiny2_content/json/en/DestinyActivityGraphDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyActivityInteractableDefinition": "/common/destiny2_content/json/en/DestinyActivityInteractableDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyBondDefinition": "/common/destiny2_content/json/en/DestinyBondDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyCharacterCustomizationCategoryDefinition": "/common/destiny2_content/json/en/DestinyCharacterCustomizationCategoryDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyCharacterCustomizationOptionDefinition": "/common/destiny2_content/json/en/DestinyCharacterCustomizationOptionDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyCollectibleDefinition": "/common/destiny2_content/json/en/DestinyCollectibleDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyDestinationDefinition": "/common/destiny2_content/json/en/DestinyDestinationDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyEntitlementOfferDefinition": "/common/destiny2_content/json/en/DestinyEntitlementOfferDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyEquipmentSlotDefinition": "/common/destiny2_content/json/en/DestinyEquipmentSlotDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyEventCardDefinition": "/common/destiny2_content/json/en/DestinyEventCardDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyFireteamFinderActivityGraphDefinition": "/common/destiny2_content/json/en/DestinyFireteamFinderActivityGraphDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyFireteamFinderActivitySetDefinition": "/common/destiny2_content/json/en/DestinyFireteamFinderActivitySetDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyFireteamFinderLabelDefinition": "/common/destiny2_content/json/en/DestinyFireteamFinderLabelDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyFireteamFinderLabelGroupDefinition": "/common/destiny2_content/json/en/DestinyFireteamFinderLabelGroupDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyFireteamFinderOptionDefinition": "/common/destiny2_content/json/en/DestinyFireteamFinderOptionDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyFireteamFinderOptionGroupDefinition": "/common/destiny2_content/json/en/DestinyFireteamFinderOptionGroupDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyStatDefinition": "/common/destiny2_content/json/en/DestinyStatDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyInventoryItemDefinition": "/common/destiny2_content/json/en/DestinyInventoryItemDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyInventoryItemLiteDefinition": "/common/destiny2_content/json/en/DestinyInventoryItemLiteDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyItemTierTypeDefinition": "/common/destiny2_content/json/en/DestinyItemTierTypeDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyLoadoutColorDefinition": "/common/destiny2_content/json/en/DestinyLoadoutColorDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyLoadoutIconDefinition": "/common/destiny2_content/json/en/DestinyLoadoutIconDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyLoadoutNameDefinition": "/common/destiny2_content/json/en/DestinyLoadoutNameDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyLocationDefinition": "/common/destiny2_content/json/en/DestinyLocationDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyLoreDefinition": "/common/destiny2_content/json/en/DestinyLoreDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyMaterialRequirementSetDefinition": "/common/destiny2_content/json/en/DestinyMaterialRequirementSetDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyMetricDefinition": "/common/destiny2_content/json/en/DestinyMetricDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyObjectiveDefinition": "/common/destiny2_content/json/en/DestinyObjectiveDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinySandboxPerkDefinition": "/common/destiny2_content/json/en/DestinySandboxPerkDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyPlatformBucketMappingDefinition": "/common/destiny2_content/json/en/DestinyPlatformBucketMappingDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyPlugSetDefinition": "/common/destiny2_content/json/en/DestinyPlugSetDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyPowerCapDefinition": "/common/destiny2_content/json/en/DestinyPowerCapDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyPresentationNodeDefinition": "/common/destiny2_content/json/en/DestinyPresentationNodeDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyProgressionDefinition": "/common/destiny2_content/json/en/DestinyProgressionDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyProgressionLevelRequirementDefinition": "/common/destiny2_content/json/en/DestinyProgressionLevelRequirementDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyRecordDefinition": "/common/destiny2_content/json/en/DestinyRecordDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyRewardAdjusterPointerDefinition": "/common/destiny2_content/json/en/DestinyRewardAdjusterPointerDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyRewardAdjusterProgressionMapDefinition": "/common/destiny2_content/json/en/DestinyRewardAdjusterProgressionMapDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyRewardItemListDefinition": "/common/destiny2_content/json/en/DestinyRewardItemListDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinySackRewardItemListDefinition": "/common/destiny2_content/json/en/DestinySackRewardItemListDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinySandboxPatternDefinition": "/common/destiny2_content/json/en/DestinySandboxPatternDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinySeasonDefinition": "/common/destiny2_content/json/en/DestinySeasonDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinySeasonPassDefinition": "/common/destiny2_content/json/en/DestinySeasonPassDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinySocialCommendationDefinition": "/common/destiny2_content/json/en/DestinySocialCommendationDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinySocketCategoryDefinition": "/common/destiny2_content/json/en/DestinySocketCategoryDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinySocketTypeDefinition": "/common/destiny2_content/json/en/DestinySocketTypeDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyTraitDefinition": "/common/destiny2_content/json/en/DestinyTraitDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyUnlockCountMappingDefinition": "/common/destiny2_content/json/en/DestinyUnlockCountMappingDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyUnlockEventDefinition": "/common/destiny2_content/json/en/DestinyUnlockEventDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyUnlockExpressionMappingDefinition": "/common/destiny2_content/json/en/DestinyUnlockExpressionMappingDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyVendorDefinition": "/common/destiny2_content/json/en/DestinyVendorDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyMilestoneDefinition": "/common/destiny2_content/json/en/DestinyMilestoneDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyActivityModifierDefinition": "/common/destiny2_content/json/en/DestinyActivityModifierDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyReportReasonCategoryDefinition": "/common/destiny2_content/json/en/DestinyReportReasonCategoryDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyArtifactDefinition": "/common/destiny2_content/json/en/DestinyArtifactDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyBreakerTypeDefinition": "/common/destiny2_content/json/en/DestinyBreakerTypeDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyChecklistDefinition": "/common/destiny2_content/json/en/DestinyChecklistDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyEnergyTypeDefinition": "/common/destiny2_content/json/en/DestinyEnergyTypeDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinySocialCommendationNodeDefinition": "/common/destiny2_content/json/en/DestinySocialCommendationNodeDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyGuardianRankDefinition": "/common/destiny2_content/json/en/DestinyGuardianRankDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyGuardianRankConstantsDefinition": "/common/destiny2_content/json/en/DestinyGuardianRankConstantsDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyLoadoutConstantsDefinition": "/common/destiny2_content/json/en/DestinyLoadoutConstantsDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
    "DestinyFireteamFinderConstantsDefinition": "/common/destiny2_content/json/en/DestinyFireteamFinderConstantsDefinition-b480d136-fa1d-4c23-b04f-3b978d639fda.json",
}


max_threshold = 1 * 1024 * 1024  # 2MB

interest_Definition_data = [
    "DestinyInventoryItemLiteDefinition",
    "DestinySandboxPerkDefinition",
    "DestinyStatDefinition",
    "DestinyInventoryBucketDefinition",
    "DestinyEquipmentSlotDefinition",
]


def split_json(file_path, threshold):
    base_name = os.path.basename(file_path)
    file_name = os.path.splitext(base_name)[0]
    dir_name = file_name + "_dir"
    output_dir = os.path.join(os.path.dirname(file_path), dir_name)
    os.makedirs(output_dir, exist_ok=True)
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    part = 1
    size = 0
    output = {}
    for key, value in data.items():
        output[key] = value
        size += len(json.dumps({key: value}))
        if size > threshold:
            save_file_path = os.path.join(output_dir, f"{file_name}_part{part}.json")
            with open(save_file_path, "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False)
            part += 1
            size = 0
            output = {}
    if output:
        save_file_path = os.path.join(output_dir, f"{file_name}_part{part}.json")
        with open(save_file_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False)
    os.remove(file_path)


def read_json_parts(file_path):
    dir_path = Path(file_path)
    file_name = dir_path.stem.split("_")[0] + "_part*.json"
    data = {}
    for entry in dir_path.iterdir():
        if entry.is_file() and fnmatch.fnmatch(entry.name, file_name):
            with open(entry, "r", encoding="utf-8") as f:
                data.update(json.load(f))
    return data


def load_local_json(file_path):
    if os.path.isfile(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    elif os.path.isdir(file_path):
        data = read_json_parts(file_path)
    else:
        data = None
    return data


def get_json_data_from_net(key, url_path):
    folder = get_real_path("Doc", "resource")
    os.makedirs(folder, exist_ok=True)

    r = requests.get(BASE_URL + url_path)

    if r.status_code == 200:
        data = r.json()
        name = key
        file_type = url_path.split(".", -1)[-1]
        file_path = os.path.join(folder, f"{name}.{file_type}")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        file_size = os.path.getsize(file_path)
        if file_size > max_threshold:
            split_json(file_path, max_threshold)
        return data
    else:
        print("load_data_fail:", r)
        print(r.json())


def check_and_load_from_net(definition_key):
    # 检查文件是否下载，如果没有，就下载
    folder = get_real_path("Doc", "resource")
    file_path = os.path.join(folder, f"{definition_key}.json")
    file_dir_path = os.path.join(folder, f"{definition_key}_dir")

    if os.path.exists(file_path):
        return load_local_json(file_path)
    elif os.path.exists(file_dir_path):
        return read_json_parts(file_dir_path)
    else:
        data = get_json_data_from_net(definition_key, component_path[definition_key])
    return data


def load_Data():
    folder = get_real_path("Doc", "resource")
    os.makedirs(folder, exist_ok=True)

    local_files = {}
    for item in os.scandir(folder):
        full_name = os.path.basename(item.path)
        file_name = os.path.splitext(full_name)[0]
        local_files[file_name] = item

    for key in interest_Definition_data:
        if key in local_files or f"{key}_dir" in local_files:
            load_local_json(item.path)
        else:
            get_json_data_from_net(key, component_path[key])
            get_json_data_from_net(f"{key}_en", component_path_en[key])


class DestinyManifestData(Singleton):
    def __init__(self):
        self._data = {}

    def get(self, key):
        if key not in self._data:
            self._data[key] = check_and_load_from_net(key)
        return self._data[key]


def get_item_bucketTypeHash_by_hash(item_hash):
    find_key = "DestinyInventoryItemLiteDefinition"
    item_hash = str(item_hash)
    destiny_manifest_data = DestinyManifestData()
    item = destiny_manifest_data.get(find_key).get(item_hash, {})
    return item.get("inventory", {}).get("bucketTypeHash")


# check_and_load_from_net("DestinyInventoryItemLiteDefinition")
# print(get_item_bucketTypeHash_by_hash("1767106452"))

# load_Data()

# BucketTypeHash = get_item_bucketTypeHash_by_hash("3423574140")
# print(BucketTypeHash)
# print(type(BucketTypeHash))
