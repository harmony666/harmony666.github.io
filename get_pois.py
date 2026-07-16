#!/usr/bin/env python3
# 含完整行程（含每晚住宿）+ 搜真实坐标 → coords.json
# 酒店类 cat=hotel，额外配色
import json, urllib.request, urllib.parse, time

KEY = "B6VBZ-V75KG-HBEQP-IRLIB-ANBLZ-W6BD5"

# (name, city, day, cat, time, title, desc)
# cat: scenic/food/culture/shop/transit/hotel
POIS = [
    # DAY 1 济南
    ("济南遥墙国际机场", "济南", 1, "transit", "11:05", "抵达济南", "航班 9:40 武汉天河→11:05 济南遥墙"),
    ("趵突泉", "济南", 1, "culture", "14:00", "趵突泉", "天下第一泉，泉城标志性名泉"),
    ("五龙潭公园", "济南", 1, "scenic", "15:30", "五龙潭公园", "清泉绿潭，闹市中的幽静园林"),
    ("泉城广场", "济南", 1, "scenic", "16:30", "泉城广场", "济南城市客厅，泉城路商圈"),
    ("芙蓉街", "济南", 1, "food", "18:00", "芙蓉街", "老城美食街，油旋/把子肉/鲁菜小吃"),
    ("大明湖", "济南", 1, "scenic", "19:30", "大明湖(夜游)", "四面荷花三面柳，夏雨荷故地"),
    # 酒店
    ("天桥区小清河北路恒大滨河左岸", "济南", 1, "hotel", "21:30", "济南住宿·天桥区", "恒大滨河左岸D9公寓(已订 ¥138)"),
    # DAY 2 济南（晚在火车，无酒店）
    ("千佛山", "济南", 2, "scenic", "09:00", "千佛山", "城东南名胜，佛教石刻与俯城视野"),
    ("山东省博物馆", "济南", 2, "culture", "11:00", "山东省博物馆", "齐鲁文明通史，亚醜钺等馆藏"),
    ("山东美术馆", "济南", 2, "culture", "13:00", "山东美术馆", "现代艺术展陈，免费参观"),
    ("洪家楼教堂", "济南", 2, "culture", "15:00", "洪家楼教堂", "华北最大哥特式天主教堂"),
    ("宽厚里", "济南", 2, "food", "18:00", "宽厚里", "古风商业街，鲁味夜宵与文创"),
    ("济南站", "济南", 2, "transit", "20:42", "济南站出发", "20:42 硬卧 Z 字头→次日 5:30 威海"),
    # DAY 3 威海
    ("威海站", "威海", 3, "transit", "05:30", "抵达威海·取车", "5:30 到站，7:00 一嗨取车(秦PLUS)"),
    ("刘公岛", "威海", 3, "culture", "09:00", "刘公岛", "甲午战争纪念地，北洋海军遗址"),
    ("威海公园", "威海", 3, "scenic", "14:00", "威海公园", "海滨带状公园，画中画地标"),
    ("幸福门广场", "威海", 3, "scenic", "15:30", "幸福门", "威海地标拱门，登高看海"),
    ("环翠楼公园", "威海", 3, "culture", "17:00", "环翠楼", "城市观景楼，俯瞰威海湾"),
    ("高新区山大路15-6号", "威海", 3, "hotel", "19:30", "威海住宿·山大路", "山大路15-6号建设银行旁(已订 ¥352)"),
    # DAY 4 威海（同上继续住）
    ("成山头", "威海", 4, "scenic", "08:00", "成山头", "天之尽头，中国大陆最东端"),
    ("那香海", "威海", 4, "scenic", "11:00", "那香海", "钻石沙滩，滨海度假带"),
    ("鸡鸣岛", "威海", 4, "scenic", "14:00", "鸡鸣岛", "海岛渔村，《爸爸去哪儿》取景"),
    ("国际海水浴场", "威海", 4, "scenic", "17:00", "国际海水浴场", "傍晚踏浪游泳，日落最美"),
    ("高新区山大路15-6号", "威海", 4, "hotel", "19:30", "威海住宿·山大路(继续住)", "继续住山大路"),
    # DAY 5 威海→烟台（烟台住我推荐）
    ("猫头山", "威海", 5, "scenic", "08:00", "猫头山", "威海最美海岸线观景公路"),
    ("烟台山", "烟台", 5, "culture", "12:00", "烟台山", "近代开埠领事馆建筑群+灯塔"),
    ("朝阳街", "烟台", 5, "food", "15:00", "朝阳街", "红酒文化街区，洋房美食"),
    ("所城里", "烟台", 5, "culture", "17:00", "所城里", "烟台古城，明代所城肌理"),
    ("烟台金海湾酒店", "烟台", 5, "hotel", "20:00", "烟台住宿·金海湾", "烟台山旁海景(推荐 ¥400)"),
    # DAY 6 烟台（继续住）
    ("养马岛", "烟台", 6, "scenic", "08:30", "养马岛", "东方马尔代夫，环岛滨海路"),
    ("蓬莱阁", "烟台", 6, "culture", "13:00", "蓬莱阁", "我国古代四大名楼，八仙故里"),
    ("八仙过海景区", "烟台", 6, "scenic", "15:30", "八仙过海景区", "海上园林，八仙过海传说地"),
    ("烟台大悦城", "烟台", 6, "shop", "19:00", "大悦城", "滨海商圈，夜生活与购物"),
    ("烟台金海湾酒店", "烟台", 6, "hotel", "21:00", "烟台住宿·金海湾(继续住)", "继续住金海湾"),
    # DAY 7 烟台→威海（威海站住我推荐）
    ("张裕酒文化博物馆", "烟台", 7, "culture", "09:00", "张裕酒文化博物馆", "中国葡萄酒工业发源地"),
    ("第一海水浴场", "烟台", 7, "scenic", "11:00", "第一海水浴场", "烟台核心浴场，沙滩漫步"),
    ("渔人码头", "烟台", 7, "shop", "13:00", "渔人码头(午餐)", "烟台山旁欧风码头，海鲜西餐"),
    ("韩乐坊", "威海", 7, "food", "18:00", "韩乐坊", "威海韩风夜市，烤肉/海鲜夜宵"),
    ("汉庭酒店威海火车站店", "威海", 7, "hotel", "20:30", "威海站住宿·汉庭", "汉庭威海火车站店(推荐 ¥150)"),
    # DAY 8 威海（修正 9:19 出发，仅早上去车站前）
    ("火炬八街", "威海", 8, "scenic", "07:00", "火炬八街", "清晨打卡威海小镰仓"),
    ("国际海水浴场", "威海", 8, "scenic", "08:00", "国际海水浴场(最后玩海)", "最后玩海，留念拍照"),
    ("威海站", "威海", 8, "transit", "09:19", "威海站发车", "9:19 硬卧→次日 5:03 武昌"),
    # DAY 9
    ("武昌站", "武汉", 9, "transit", "05:03", "抵达武昌", "行程结束，平安到家"),
]

def poi_search(name, city):
    url = ("https://apis.map.qq.com/ws/place/v1/search?key=" + KEY
           + "&page_size=5&keyword=" + urllib.parse.quote(name)
           + "&boundary=" + urllib.parse.quote("region(" + city + ",0)"))
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8"))
        if data.get("status") == 0 and data.get("data"):
            top = data["data"][0]
            return {"lat": top["location"]["lat"], "lng": top["location"]["lng"], "found": top["title"]}
    except Exception as e:
        return {"error": "poi:" + str(e)}
    return {"error": "poi not found"}

def geocode(address, city):
    url = ("https://apis.map.qq.com/ws/geocoder/v1/?key=" + KEY
           + "&address=" + urllib.parse.quote(address + " " + city))
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8"))
        if data.get("status") == 0 and data.get("result") and data["result"].get("location"):
            loc = data["result"]["location"]
            return {"lat": loc["lat"], "lng": loc["lng"], "found": data["result"].get("title", address)}
    except Exception as e:
        return {"error": "geo:" + str(e)}
    return {"error": "geo not found"}

def search(name, city):
    r = poi_search(name, city)
    if "lat" in r: return r
    r2 = geocode(name, city)
    if "lat" in r2: return r2
    return {"error": r.get("error","?") + " | " + r2.get("error","?")}

results = []
for name, city, day, cat, tm, title, desc in POIS:
    r = search(name, city)
    rec = {"name": name, "city": city, "day": day, "cat": cat, "time": tm, "title": title, "desc": desc}
    rec.update(r)
    results.append(rec)
    print(f"[D{day}] {name} -> {r.get('lat')},{r.get('lng')}  ({r.get('found', r.get('error'))})", flush=True)
    time.sleep(0.25)

# 同日编号
groups = {}
for r in results:
    groups.setdefault(r["day"], []).append(r)
for d, lst in groups.items():
    for i, p in enumerate(lst, 1):
        p["num"] = i

with open("coords.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("SAVED coords.json, total", len(results))
