import base64
import hashlib
import json
import pathlib
from datetime import datetime
from typing import Dict, Optional

import geoip2.database
import user_agents
from aws_lambda_powertools import Logger
from ua_parser import user_agent_parser

logger = Logger()
lambda_dir = pathlib.Path(__file__).parent.resolve()

geoip_db_reader = geoip2.database.Reader(lambda_dir.joinpath("GeoLite2-City.mmdb"))

def get_device_type(headers: Dict) -> str:
    mapping = [
        ("CloudFront-Is-Mobile-Viewer", "mobile"),
        ("CloudFront-Is-Desktop-Viewer", "desktop"),
        ("CloudFront-Is-SmartTV-Viewer", "smarttv"),
        ("CloudFront-Is-Tablet-Viewer", "tablet"),
    ]

    for header, device_type in mapping:
        if headers.get(header) == "true":
            return device_type

    return "unknown"


def get_geo_from_ip(ip_address: str) -> Optional[Dict]:
    try:
        geoip = geoip_db_reader.city(ip_address)
        geoip_data = {
            "country": {"name": geoip.country.name, "iso": geoip.country.iso_code},
            "city": geoip.city.name,
        }
        return geoip_data
    except Exception:
        logger.error("Failed to retrieve geo information", exc_info=True)
        return None

def process_record(record: Dict) -> Optional[Dict]:
    headers = record["headers"]
    identity = record["identity"]

    body = record["body"]
    body["event_id"] = identity["requestId"]
    body["request_time"] = datetime.utcfromtimestamp(
        record["request_time"] / 1000
    ).isoformat()
    

    user_data = {}
    if len(identity["userAgent"]) > 0:
        try:
            ua = user_agents.parse(identity["userAgent"])
            browser = ua.browser.family + (
                " " + ua.browser.version_string if ua.browser.version_string else ""
            )
            os_ = ua.os.family + (
                " " + ua.os.version_string if ua.os.version_string else ""
            )

            user_data["browser"] = browser
            user_data["operating_system"] = os_

            if ua.is_bot:
                logger.info("Blocked event from bot: %s", browser)
                return None

        except Exception:
            logger.error("Failed to set data from user agent", exc_info=True)

    user_data["geoip"] = get_geo_from_ip(identity["sourceIp"])
    ip = identity["sourceIp"]
    ua = identity["userAgent"]
    user_data["fingerprint"] = hashlib.md5((ip + ua).encode("utf-8")).hexdigest()
    user_data["device_type"] = get_device_type(headers)

    body["user_data"] = user_data

    # Body: {record["body"]: Dict, request_time: timestamp, event_id: str, user_data: Dict}
    return body


def handler(event, context):
    output = []

    for record in event["records"]:
        logger.info("Record ID: %s", record["recordId"])
        payload = json.loads(base64.b64decode(record["data"]).decode("utf-8"))

        logger.info(
            "Payload: %s", payload
        ) 
        processed_event = process_record(payload)
        logger.info("Processed event: %s", processed_event)

        # Don't add filtered out (None) events to the output
        if processed_event:
            result_payload = json.dumps(processed_event)
            output_record = {
                "recordId": record["recordId"],
                "result": "Ok",
                "data": base64.b64encode(result_payload.encode("utf-8")),
            }
            output.append(output_record)
        else:
            output.append(
                {
                    "recordId": record["recordId"],
                    "result": "Dropped",
                }
            )

    logger.info("Successfully processed %d records.", len(event["records"]))

    return {"records": output}