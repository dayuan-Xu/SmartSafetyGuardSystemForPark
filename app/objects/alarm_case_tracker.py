import os
import time
from datetime import datetime
from collections import defaultdict
from app.utils.my_utils import get_now

# 读取防抖配置
DEBOUNCE_NORMAL_TO_VIOLATION = int(os.getenv("DEBOUNCE_NORMAL_TO_VIOLATION", 2))
DEBOUNCE_VIOLATION_TO_NORMAL = int(os.getenv("DEBOUNCE_VIOLATION_TO_NORMAL", 3))

class DebouncedAlarmCaseTracker:
    def __init__(self):
        # 存储一个实时帧每个告警场景的完整状态（基础状态+防抖信息）
        # 结构：{
        #   alarm_case_source: {
        #       "current_state": bool,          # 当前确认的状态（True=告警）
        #       "pending_state": bool,          # 待确认的状态（可能与current_state不同）
        #       "debounce_start_time": datetime,# 待确认状态第一次不同于current_state的时间（用于计算防抖窗口）
        #       "alarm_id": int                 # 关联的告警ID
        #   }
        # }
        self.alarm_case_states = defaultdict(self._init_alarm_case_state)

    @staticmethod
    def _init_alarm_case_state():
        """初始化单个告警场景的状态"""
        return {
            "current_state": False,         # type: bool            # 当前确认状态（True=告警场景检测到）
            "pending_state": None,          # type: bool | None     # 待确认状态（如果不为None，则其bool值与current_state相反）
            "debounce_start_time": None,    # type: datetime | None # 待确认状态的开始时间（用于计算防抖窗口）
            "alarm_id": None                # type: int | None      # 关联的告警ID
        }

    def update_state(self, alarm_case_source, alarm_case_detected):
        """
        输入:
        alarm_case_source:当前告警场景的来源
        alarm_case_detected:单帧检测结果，True或者False，表示检测到告警场景or没有检测到
        返回:
        确认后的当前状态（含防抖逻辑）

        返回值：{
            "confirmed_state": bool,          # 确认后的当前状态
            "state_changed": bool,            # 是否确认发生了状态切换
            "change_type": str,               # 切换类型："normal_to_violation"/"violation_to_normal"/None
            "alarm_id": int                   # 当前关联的告警ID
        }
        """
        # 获取当前告警场景状态的引用，如果不存在则初始化
        state = self.alarm_case_states[alarm_case_source]
        current_time = get_now()
        result = {
            "confirmed_state": state["current_state"],
            "state_changed": False,
            "change_type": None,
            "alarm_id": state["alarm_id"]
        }

        # 1. 检测结果与当前确认状态一致：无需防抖，重置待确认状态
        if alarm_case_detected == state["current_state"]:
            state["pending_state"] = None
            state["debounce_start_time"] = None
            return result

        # 2. 检测结果与当前确认状态不一致：进入防抖流程
        # 2.1 首次出现不一致：记录待确认状态和防抖开始时间
        if state["pending_state"] is None:
            state["pending_state"] = alarm_case_detected
            state["debounce_start_time"] = current_time
            return result

        # 2.2 已存在待确认状态：检查是否满足防抖时间窗口
        debounce_duration = (current_time - state["debounce_start_time"]).total_seconds()
        # 确定当前场景的防抖阈值（正常→告警 或 告警→正常）
        if state["current_state"] is False and alarm_case_detected is True:
            # 场景1：正常→告警，用对应阈值
            required_debounce = DEBOUNCE_NORMAL_TO_VIOLATION
            target_change_type = "normal_to_violation"
        else:
            # 场景2：告警→正常，用对应阈值
            required_debounce = DEBOUNCE_VIOLATION_TO_NORMAL
            target_change_type = "violation_to_normal"

        # 2.3 防抖时间未达标：继续等待（需确保检测结果持续为待确认状态）
        if debounce_duration < required_debounce:
            # 若中途检测结果变回原状态，重置防抖（此处已通过步骤1处理，可省略）
            return result

        # 2.4 防抖时间达标：确认状态切换，构造返回结果
        state["current_state"] = state["pending_state"]
        state["pending_state"] = None
        state["debounce_start_time"] = None
        result["confirmed_state"] = state["current_state"]
        result["state_changed"] = True
        result["change_type"] = target_change_type

        return result

    def bind_alarm_id(self, alarm_case_source, alarm_id):
        """将告警ID与当前告警状态绑定（用于后续更新告警记录）"""
        self.alarm_case_states[alarm_case_source]["alarm_id"] = alarm_id
