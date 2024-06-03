URL_BASE = "https://www.bungie.net/platform"
ACCESS_TOKEN = None
ACCESS_TOKEN_TIME_OUT = 3600


class ClassType:
    Titan = 0
    Hunter = 1
    Warlock = 2


ClassTypeMap = {"Titan": ClassType.Titan, "Hunter": ClassType.Hunter, "Warlock": ClassType.Warlock}


class BucketHash:
    post_master = 215593132


class StatHush:
    Intellect = 144602215  # 智慧
    Resilience = 392767087  # 韧性
    Discipline = 1735777505  # 纪律
    Recovery = 1943323491  # 恢复
    Mobility = 2996146975  # 敏捷
    Strength = 4244567218  # 力量


SandboxPerkRequirement = [
    139007474,
]


# 护甲的位置 头盔 臂铠
ArmorBucketTypeHash = [3448274439, 3551918588, 14239492, 20886954, 1585787867]
