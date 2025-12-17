from __future__ import annotations

import json
import pandas as pd
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional



def read_businfo_xml(xml_path: str) -> pd.DataFrame:
    ns = {'ptx': 'https://ptx.transportdata.tw/standard/schema/'}

    tree = ET.parse(xml_path)
    root = tree.getroot()

    def t(elem: Optional[ET.Element], path: str) -> Optional[str]:
        if elem is None:
            return None
        return elem.findtext(path, default=None, namespaces=ns)

    def as_int(x: Optional[str]) -> Optional[int]:
        if x is None or x == "":
            return None
        try:
            return int(x)
        except ValueError:
            return None

    def parse_operators(route_elem: ET.Element) -> List[Dict[str, Any]]:
        ops = []
        for op in route_elem.findall('ptx:Operators/ptx:Operator', ns):
            ops.append({
                "OperatorID": t(op, 'ptx:OperatorID'),
                "OperatorNameZh": t(op, 'ptx:OperatorName/ptx:Zh_tw'),
                "OperatorNameEn": t(op, 'ptx:OperatorName/ptx:En'),
                "OperatorCode": t(op, 'ptx:OperatorCode'),
                "OperatorNo": t(op, 'ptx:OperatorNo'),
            })
        return ops

    def parse_subroute_operator_ids(sub_elem: ET.Element) -> List[str]:
        ids = []
        for opid in sub_elem.findall('ptx:OperatorIDs/ptx:OperatorID', ns):
            if opid.text and opid.text.strip():
                ids.append(opid.text.strip())
        return ids

    rows: List[Dict[str, Any]] = []

    for route in root.findall('ptx:BusRoute', ns):
        ops = parse_operators(route)
        ops_json = json.dumps(ops, ensure_ascii=False)
        op0 = ops[0] if ops else {}

        # Route-level (swagger order)
        base = {
            "RouteUID": t(route, 'ptx:RouteUID'),
            "RouteID": t(route, 'ptx:RouteID'),
            "HasSubRoutes": t(route, 'ptx:HasSubRoutes'),
            # Operators (保留完整 + 常用第一筆)
            "Operators_json": ops_json,
            "OperatorID_first": op0.get("OperatorID"),
            "OperatorNameZh_first": op0.get("OperatorNameZh"),
            "OperatorNameEn_first": op0.get("OperatorNameEn"),
            "OperatorCode_first": op0.get("OperatorCode"),
            "OperatorNo_first": op0.get("OperatorNo"),
            # Authority/Provider
            "AuthorityID": t(route, 'ptx:AuthorityID'),
            "ProviderID": t(route, 'ptx:ProviderID'),
        }

        subroutes = route.findall('ptx:SubRoutes/ptx:SubRoute', ns)

        # 若真的沒有 SubRoute，就輸出一列（其餘 SubRoute 欄位補 None）
        if not subroutes:
            rows.append({
                **base,
                "SubRouteUID": None,
                "SubRouteID": None,
                "OperatorIDs": [],
                "SubRouteNameZh": None,
                "SubRouteNameEn": None,
                "Headsign": None,
                "HeadsignEn": None,
                "Direction": None,
                "FirstBusTime": None,
                "LastBusTime": None,
                "HolidayFirstBusTime": None,
                "HolidayLastBusTime": None,
                "SubDepartureStopNameZh": None,
                "SubDepartureStopNameEn": None,
                "SubDestinationStopNameZh": None,
                "SubDestinationStopNameEn": None,

                "BusRouteType": as_int(t(route, 'ptx:BusRouteType')),
                "RouteNameZh": t(route, 'ptx:RouteName/ptx:Zh_tw'),
                "RouteNameEn": t(route, 'ptx:RouteName/ptx:En'),
                "DepartureStopNameZh": t(route, 'ptx:DepartureStopNameZh'),
                "DepartureStopNameEn": t(route, 'ptx:DepartureStopNameEn'),
                "DestinationStopNameZh": t(route, 'ptx:DestinationStopNameZh'),
                "DestinationStopNameEn": t(route, 'ptx:DestinationStopNameEn'),
                "TicketPriceDescriptionZh": t(route, 'ptx:TicketPriceDescriptionZh'),
                "TicketPriceDescriptionEn": t(route, 'ptx:TicketPriceDescriptionEn'),
                "FareBufferZoneDescriptionZh": t(route, 'ptx:FareBufferZoneDescriptionZh'),
                "FareBufferZoneDescriptionEn": t(route, 'ptx:FareBufferZoneDescriptionEn'),
                "RouteMapImageUrl": t(route, 'ptx:RouteMapImageUrl'),
                "City": t(route, 'ptx:City'),
                "CityCode": t(route, 'ptx:CityCode'),
                "UpdateTime": t(route, 'ptx:UpdateTime'),
                "VersionID": as_int(t(route, 'ptx:VersionID')),
            })
            continue

        for sub in subroutes:
            operator_ids = parse_subroute_operator_ids(sub)

            rows.append({
                **base,

                # SubRoutes (swagger order)
                "SubRouteUID": t(sub, 'ptx:SubRouteUID'),
                "SubRouteID": t(sub, 'ptx:SubRouteID'),
                "OperatorIDs": operator_ids,
                "SubRouteNameZh": t(sub, 'ptx:SubRouteName/ptx:Zh_tw'),
                "SubRouteNameEn": t(sub, 'ptx:SubRouteName/ptx:En'),
                "Headsign": t(sub, 'ptx:Headsign'),
                "HeadsignEn": t(sub, 'ptx:HeadsignEn'),
                "Direction": as_int(t(sub, 'ptx:Direction')),
                "FirstBusTime": t(sub, 'ptx:FirstBusTime'),
                "LastBusTime": t(sub, 'ptx:LastBusTime'),
                "HolidayFirstBusTime": t(sub, 'ptx:HolidayFirstBusTime'),
                "HolidayLastBusTime": t(sub, 'ptx:HolidayLastBusTime'),
                "SubDepartureStopNameZh": t(sub, 'ptx:DepartureStopNameZh'),
                "SubDepartureStopNameEn": t(sub, 'ptx:DepartureStopNameEn'),
                "SubDestinationStopNameZh": t(sub, 'ptx:DestinationStopNameZh'),
                "SubDestinationStopNameEn": t(sub, 'ptx:DestinationStopNameEn'),

                # Route remaining fields (swagger order)
                "BusRouteType": as_int(t(route, 'ptx:BusRouteType')),
                "RouteNameZh": t(route, 'ptx:RouteName/ptx:Zh_tw'),
                "RouteNameEn": t(route, 'ptx:RouteName/ptx:En'),
                "DepartureStopNameZh": t(route, 'ptx:DepartureStopNameZh'),
                "DepartureStopNameEn": t(route, 'ptx:DepartureStopNameEn'),
                "DestinationStopNameZh": t(route, 'ptx:DestinationStopNameZh'),
                "DestinationStopNameEn": t(route, 'ptx:DestinationStopNameEn'),
                "TicketPriceDescriptionZh": t(route, 'ptx:TicketPriceDescriptionZh'),
                "TicketPriceDescriptionEn": t(route, 'ptx:TicketPriceDescriptionEn'),
                "FareBufferZoneDescriptionZh": t(route, 'ptx:FareBufferZoneDescriptionZh'),
                "FareBufferZoneDescriptionEn": t(route, 'ptx:FareBufferZoneDescriptionEn'),
                "RouteMapImageUrl": t(route, 'ptx:RouteMapImageUrl'),
                "City": t(route, 'ptx:City'),
                "CityCode": t(route, 'ptx:CityCode'),
                "UpdateTime": t(route, 'ptx:UpdateTime'),
                "VersionID": as_int(t(route, 'ptx:VersionID')),
            })

    df = pd.DataFrame(rows)

    # 依 swagger 順序強制排欄位（你要的重點）
    desired_cols = [
        # BusRoute
        "RouteUID", "RouteID", "HasSubRoutes",
        # Operators（swagger 原本是 array；我加了兩種表示法）
        "Operators_json", "OperatorID_first", "OperatorNameZh_first", "OperatorNameEn_first",
        "OperatorCode_first", "OperatorNo_first",
        # Authority/Provider
        "AuthorityID", "ProviderID",
        # SubRoutes（swagger order）
        "SubRouteUID", "SubRouteID", "OperatorIDs", "SubRouteNameZh", "SubRouteNameEn",
        "Headsign", "HeadsignEn", "Direction",
        "FirstBusTime", "LastBusTime", "HolidayFirstBusTime", "HolidayLastBusTime",
        "SubDepartureStopNameZh", "SubDepartureStopNameEn",
        "SubDestinationStopNameZh", "SubDestinationStopNameEn",
        # Remaining route fields (swagger order)
        "BusRouteType",
        "RouteNameZh", "RouteNameEn",
        "DepartureStopNameZh", "DepartureStopNameEn",
        "DestinationStopNameZh", "DestinationStopNameEn",
        "TicketPriceDescriptionZh", "TicketPriceDescriptionEn",
        "FareBufferZoneDescriptionZh", "FareBufferZoneDescriptionEn",
        "RouteMapImageUrl",
        "City", "CityCode",
        "UpdateTime", "VersionID",
    ]

    # 補齊缺的欄位（避免某些 XML 沒出現導致 KeyError）
    for c in desired_cols:
        if c not in df.columns:
            df[c] = None

    df = df[desired_cols]

    # Optional: HasSubRoutes 轉 bool
    df["HasSubRoutes"] = df["HasSubRoutes"].map(
        lambda x: True if str(x).lower() == "true" else False if str(x).lower() == "false" else None
    )

    return df

def read_bus_stop_of_route_xml(xml_path: str) -> pd.DataFrame:
    """
    讀取 TDX 公車站序 XML（BusStopOfRoute），回傳整理好的 pandas DataFrame。
    
    每一列 = 一個站牌（Stop），同時附上路線 / 營運業者資訊。
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # 自動從 root 解析出 namespace（避免寫死）
    if root.tag.startswith("{"):
        uri = root.tag.split("}")[0].strip("{")
    else:
        uri = "https://ptx.transportdata.tw/standard/schema/"
    ns = {"ns": uri}

    def gettext(elem, path):
        """安全取 text，找不到就回 None"""
        if elem is None:
            return None
        child = elem.find(path, ns)
        return child.text if child is not None else None

    rows = []

    # 每一個 <BusStopOfRoute> 代表一條路線 + 方向
    for bsr in root.findall("ns:BusStopOfRoute", ns):

        # 路線共同欄位
        base = {
            "RouteUID":          gettext(bsr, "ns:RouteUID"),
            "RouteID":           gettext(bsr, "ns:RouteID"),
            "RouteName_Zh":      gettext(bsr, "ns:RouteName/ns:Zh_tw"),
            "RouteName_En":      gettext(bsr, "ns:RouteName/ns:En"),
            "SubRouteUID":       gettext(bsr, "ns:SubRouteUID"),
            "SubRouteID":        gettext(bsr, "ns:SubRouteID"),
            "SubRouteName_Zh":   gettext(bsr, "ns:SubRouteName/ns:Zh_tw"),
            "SubRouteName_En":   gettext(bsr, "ns:SubRouteName/ns:En"),
            "Direction":         gettext(bsr, "ns:Direction"),
            "City":              gettext(bsr, "ns:City"),
            "CityCode":          gettext(bsr, "ns:CityCode"),
            "OperatorID":        gettext(bsr, "ns:Operators/ns:Operator/ns:OperatorID"),
            "OperatorName_Zh":   gettext(bsr, "ns:Operators/ns:Operator/ns:OperatorName/ns:Zh_tw"),
            "OperatorNo":        gettext(bsr, "ns:Operators/ns:Operator/ns:OperatorNo"),
        }

        # 底下所有 <Stop>
        for stop in bsr.findall("ns:Stops/ns:Stop", ns):
            row = base.copy()
            row.update({
                "StopUID":          gettext(stop, "ns:StopUID"),
                "StopID":           gettext(stop, "ns:StopID"),
                "StopName_Zh":      gettext(stop, "ns:StopName/ns:Zh_tw"),
                "StopName_En":      gettext(stop, "ns:StopName/ns:En"),
                "StopBoarding":     gettext(stop, "ns:StopBoarding"),
                "StopSequence":     gettext(stop, "ns:StopSequence"),
                "PositionLon":      gettext(stop, "ns:StopPosition/ns:PositionLon"),
                "PositionLat":      gettext(stop, "ns:StopPosition/ns:PositionLat"),
                "GeoHash":          gettext(stop, "ns:StopPosition/ns:GeoHash"),
                "StationID":        gettext(stop, "ns:StationID"),
                "StationGroupID":   gettext(stop, "ns:StationGroupID"),
                "LocationCityCode": gettext(stop, "ns:LocationCityCode"),
            })
            rows.append(row)

    df = pd.DataFrame(rows)

    # 可選：把數值欄位轉型（如果你需要的話）
    for col in ["StopSequence"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")
    for col in ["PositionLon", "PositionLat"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

    return df

def read_bus_shape_of_route_xml(xml_path: str) -> pd.DataFrame:
    """
    讀取 TDX 公車路線 XML（BusShape），回傳整理好的 pandas DataFrame。
    """

    # 解析 XML
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # 宣告 XML namespace（必須！）
    ns = {'ns': "https://ptx.transportdata.tw/standard/schema/"}

    records = []

    # 每一個 <BusShape> 就是一筆資料
    for bus in root.findall('ns:BusShape', ns):
        record = {
            "Geometry": bus.findtext('ns:Geometry', namespaces=ns),
            "EncodedPolyline": bus.findtext('ns:EncodedPolyline', namespaces=ns),
            "RouteUID": bus.findtext('ns:RouteUID', namespaces=ns),
            "RouteID": bus.findtext('ns:RouteID', namespaces=ns),
            "RouteName_Zh": bus.find('ns:RouteName/ns:Zh_tw', ns).text if bus.find('ns:RouteName/ns:Zh_tw', ns) is not None else None,
            "RouteName_En": bus.find('ns:RouteName/ns:En', ns).text if bus.find('ns:RouteName/ns:En', ns) is not None else None,
            "SubRouteUID": bus.findtext('ns:SubRouteUID', namespaces=ns),
            "SubRouteID": bus.findtext('ns:SubRouteID', namespaces=ns),
            "SubRouteName_Zh": bus.find('ns:SubRouteName/ns:Zh_tw', ns).text if bus.find('ns:SubRouteName/ns:Zh_tw', ns) is not None else None,
            "SubRouteName_En": bus.find('ns:SubRouteName/ns:En', ns).text if bus.find('ns:SubRouteName/ns:En', ns) is not None else None,
            "Direction": bus.findtext('ns:Direction', namespaces=ns),
            "UpdateTime": bus.findtext('ns:UpdateTime', namespaces=ns),
            "VersionID": bus.findtext('ns:VersionID', namespaces=ns),
        }
        records.append(record)

    # 轉成 DataFrame
    df = pd.DataFrame(records)

    return df
