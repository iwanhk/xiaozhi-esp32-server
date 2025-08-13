import threading
from config.logger import setup_logging

# 设置日志
logger = setup_logging()
TAG = "TTSLimiter"

# 线程安全的字典，用于存储每个设备的TTS使用情况
# 格式: { "device_id": character_count }
tts_usage = {}
lock = threading.Lock()

# TTS字符数限制
TTS_CHAR_LIMIT = 10000

def check_and_update_usage(device_id: str, text_length: int) -> bool:
    """
    检查并更新设备的TTS字符使用量。

    Args:
        device_id: 设备的MAC地址。
        text_length: 本次TTS请求的字符数。

    Returns:
        bool: 如果未超过限制则返回True，否则返回False。
    """
    if not device_id:
        logger.bind(tag=TAG).warning("device_id is not provided, cannot apply TTS limit.")
        return True  # 如果没有device_id，则不限制

    with lock:
        current_usage = tts_usage.get(device_id, 0)

        if current_usage >= TTS_CHAR_LIMIT:
            logger.bind(tag=TAG).warning(f"Device {device_id} has exceeded the TTS limit of {TTS_CHAR_LIMIT} characters. Current usage: {current_usage}.")
            return False

        if current_usage + text_length > TTS_CHAR_LIMIT:
            # 即使本次超出，也先将剩余的额度用完
            tts_usage[device_id] = TTS_CHAR_LIMIT
            logger.bind(tag=TAG).warning(f"Device {device_id} will exceed TTS limit after this request. Approving this last request.")
            return True
        
        tts_usage[device_id] = current_usage + text_length
        # logger.bind(tag=TAG).info(f"Device {device_id} TTS usage updated. New usage: {tts_usage[device_id]}")
        return True

def get_usage(device_id: str) -> int:
    """
    获取指定设备的当前TTS使用量。

    Args:
        device_id: 设备的MAC地址。

    Returns:
        int: 当前已使用的字符数。
    """
    with lock:
        return tts_usage.get(device_id, 0)

