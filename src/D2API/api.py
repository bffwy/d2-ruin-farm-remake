import sys
import os

# parent_dir_name = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(parent_dir_name)

import requests
import json
import time
import random
import threading
from loguru import logger
from collections import defaultdict

from D2API import CONST, config
from D2API.LoadDoc import get_item_bucketTypeHash_by_hash


last_update_token_time = None

COMMON_HEADERS = {
    "X-API-Key": config.dim_settings.x_api_key,
    "Content-Type": "application/json",
}
characters = {}
character_items = {}

not_valid_items = {}


def get_access_token_first():
    """第一次获取 玩家token"""
    from requests.auth import HTTPBasicAuth

    url = "https://www.bungie.net/platform/app/oauth/token"
    payload = {"grant_type": "authorization_code", "code": config.dim_settings.code}
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.request(
        "POST",
        url,
        headers=headers,
        data=payload,
        auth=HTTPBasicAuth(config.dim_settings.client_id, config.dim_settings.client_secret),
    )

    if response.status_code == 200:
        response_data = response.json()

        CONST.ACCESS_TOKEN = response_data["access_token"]
        logger.info(f"ACCESS_TOKEN_get: {CONST.ACCESS_TOKEN}")
        COMMON_HEADERS["Authorization"] = "Bearer " + CONST.ACCESS_TOKEN

        refresh_token = response_data["refresh_token"]
        logger.info(f"refresh_token update: {refresh_token}")
        config.update_refresh_token(refresh_token)
        return True


def check_and_refresh_token():
    """检查 和 更新token"""
    now = time.monotonic()
    global last_update_token_time

    if not last_update_token_time or now - last_update_token_time >= CONST.ACCESS_TOKEN_TIME_OUT:
        if update_access_token():
            last_update_token_time = now


def update_access_token():
    """检查 和 更新 玩家token"""
    from requests.auth import HTTPBasicAuth

    if not config.dim_settings.refresh_token:
        get_access_token_first()
        return True

    url = "https://www.bungie.net/platform/app/oauth/token"
    payload = {"grant_type": "refresh_token", "refresh_token": config.dim_settings.refresh_token}
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.request(
        "POST",
        url,
        headers=headers,
        data=payload,
        auth=HTTPBasicAuth(config.dim_settings.client_id, config.dim_settings.client_secret),
    )

    if response.status_code == 200:
        response_data = response.json()
        CONST.ACCESS_TOKEN = response_data["access_token"]
        logger.info(f"ACCESS_TOKEN_update: {CONST.ACCESS_TOKEN}")
        COMMON_HEADERS["Authorization"] = "Bearer " + CONST.ACCESS_TOKEN

        refresh_token = response_data["refresh_token"]
        logger.info(f"refresh_token update: {refresh_token}")
        config.update_refresh_token(refresh_token)
        return True


def get_characters():
    """获取 所有角色"""
    api_path = f"/Destiny2/{config.dim_settings.membership_type}/Profile/{config.dim_settings.destiny_membership_id}/?components=200"
    r = requests.get(CONST.URL_BASE + api_path, headers=COMMON_HEADERS)
    if r.status_code == 200:
        try:
            data = r.json()
            character_data = data["Response"]["characters"]["data"]
            for character_id, character in character_data.items():
                class_type = character["classType"]
                characters[class_type] = character
        except Exception as e:
            pass


def get_item_common_data(item_id):
    # 暂时没有用。开始以为物品位置的映射再这里
    api_path = f"/Destiny2/{config.dim_settings.membership_type}/Profile/{config.dim_settings.destiny_membership_id}/Item/{item_id}?components=302,304,300,305,307"
    path = CONST.URL_BASE + api_path
    r = requests.get(path, headers=COMMON_HEADERS)
    if r.status_code == 200:
        data = r.json()
        return data["Response"]


def get_item_in_postmaster(character_id):
    """获取 角色 物品 （带在身上的）"""

    def classify_items(items):
        bucket_hash_items = defaultdict(list)
        for item in items:
            bucketHash = item["bucketHash"]
            bucket_hash_items[bucketHash].append(item)
        print("classify_items: ", bucket_hash_items.keys())
        character_items[character_id] = bucket_hash_items

    api_path = f"/Destiny2/{config.dim_settings.membership_type}/Profile/{config.dim_settings.destiny_membership_id}/Character/{character_id}?components=201"

    r = requests.get(CONST.URL_BASE + api_path, headers=COMMON_HEADERS)
    if r.status_code == 200:
        data = r.json()
        postmaster_item = []
        items = data["Response"]["inventory"]["data"]["items"]
        classify_items(items)
        for item in items:
            bucketHash = item["bucketHash"]
            quantity = item["quantity"]
            if bucketHash == CONST.BucketHash.post_master and quantity == 1:
                # 914746494 至高记忆水晶
                if item["transferStatus"] != 2 or 914746494 == item["itemHash"]:
                    postmaster_item.append(item)
        return postmaster_item
    return []


def pull_item_from_postmaster(item, character_id):
    """从 邮政管 拿物品"""
    api_path = "/Destiny2/Actions/Items/PullFromPostmaster/"

    item_id = item["itemInstanceId"]
    item_hash = item["itemHash"]
    payload = {
        "characterId": character_id,
        "membershipType": config.dim_settings.membership_type,
        "itemId": item_id,
        "transferToVault": True,
        "stackSize": 1,
        "itemReferenceHash": item_hash,
    }

    data = json.dumps(payload)
    r = requests.post(CONST.URL_BASE + api_path, headers=COMMON_HEADERS, data=data)
    print(f"PullFromPostmaster:{item_id}")
    if r.status_code == 200:
        return True


def dim_pull_item_from_postmaster(item, character_id, try_remove_item=True):
    """
    模拟 DIM 的操作
    尝试从 邮政官 拿， 失败的话，就找到这个item队友的位置，然后从这个位置里面随机拿一件物品放到保险库，
    再重新从邮政官拿物品，成功再把物品放到保险库
    """

    global character_items
    if not check_before_move(item):
        not_valid_items[item["itemInstanceId"]] = 1
        return
    ret = pull_item_from_postmaster(item, character_id)
    logger.info(f"pull_item_from_postmaster item_id={item['itemInstanceId']} ret={ret}")
    if ret:
        trans_item_to_vault(item, character_id)
    elif try_remove_item:
        item_hash = item["itemHash"]
        local_bucketHash = get_item_bucketTypeHash_by_hash(item_hash)
        current_items = character_items.get(character_id, {}).get(local_bucketHash)
        if current_items:
            pre_item = random.choice(current_items)
            trans_item_to_vault(pre_item, character_id)
            dim_pull_item_from_postmaster(item, character_id, try_remove_item=False)


def trans_item_to_vault(item, character_id):
    """把物品放到 保险库"""
    api_path = "/Destiny2/Actions/Items/TransferItem/"

    item_id = item["itemInstanceId"]
    item_hash = item["itemHash"]
    payload = {
        "characterId": character_id,
        "membershipType": config.dim_settings.membership_type,
        "itemId": item_id,
        "transferToVault": True,
        "stackSize": 1,
        "itemReferenceHash": item_hash,
    }
    data = json.dumps(payload)
    r = requests.post(CONST.URL_BASE + api_path, headers=COMMON_HEADERS, data=data)
    print(f"TransferItem: {item_id},,ret.status_code={r.status_code}")


def check_before_move(item):
    # 先检查护甲属性 是否满足要求
    # 总和 65 以上 and 力量 == 2
    # 韧性纪律 32
    # 单项 30
    item_id = item["itemInstanceId"]
    item_hash = item["itemHash"]

    if item_id in not_valid_items:
        return False

    if int(item_hash) in config.dim_settings.filter_items:
        # 拜龙教镰刀 弓箭
        return False

    item_bucket_type_hash = get_item_bucketTypeHash_by_hash(item_hash)
    logger.info(f"item: {item_bucket_type_hash}")
    if int(item_bucket_type_hash) not in CONST.ArmorBucketTypeHash:
        return True

    item_data = get_item_common_data(item_id)

    if item_data:
        try:
            stats_data = item_data["stats"]["data"]["stats"]
            count = 0
            hash_value_mal = {}
            for statHush, hash_value in stats_data.items():
                value = hash_value["value"]
                hash_value_mal[statHush] = value
                count += int(value)
            # logger.info(f"item_stat: {hash_value_mal}")
            # if hash_value_mal[str(CONST.StatHush.Resilience)] + hash_value_mal[str(CONST.StatHush.Mobility)] == 32:
            #     return True
            # if any(value == 30 for value in hash_value.values()):
            #     return True
            # return count >= 65 and hash_value_mal[str(CONST.StatHush.Strength)] == 2
            return count >= config.dim_settings.armor_sum_required

        except Exception as e:
            pass

    return True


def real_move_items_from_postmaster_to_vault():

    def move_item_postmaster_for_character(character_id):
        items = get_item_in_postmaster(character_id)
        logger.info(f"get_item_in_postmaster: character_id={character_id},,num={len(items)}")
        if not items:
            return
        for item in items:

            try:
                dim_pull_item_from_postmaster(item, character_id)
            except Exception as e:
                continue

    check_and_refresh_token()
    get_characters()
    get_postmaster_class = set(config.dim_settings.get_postmaster_class)
    for class_name in get_postmaster_class:
        class_type = CONST.ClassTypeMap.get(class_name)
        if class_type in characters:
            character = characters[class_type]
            character_id = character["characterId"]
            move_item_postmaster_for_character(character_id)


def move_items_from_postmaster_to_vault():
    t = threading.Thread(target=real_move_items_from_postmaster_to_vault)
    t.start()


def test():
    global last_update_token_time
    last_update_token_time = time.monotonic()
    CONST.ACCESS_TOKEN = ""
    COMMON_HEADERS["Authorization"] = "Bearer " + CONST.ACCESS_TOKEN
    # real_move_items_from_postmaster_to_vault()
    data = get_item_common_data(6917530009394349199)
    item_data = data["item"]["data"]
    # check_before_move(item_data)


# update_access_token()
# test()
# real_move_items_from_postmaster_to_vault()
