import cv2
import socket
import json
import time
from enum import Enum
from ultralytics import YOLO

# ================= 1. 配置参数区域 =================
PI_IP = "10.189.44.97"
VIDEO_URL = f"http://{PI_IP}:5000/video_feed"
PI_CMD_PORT = 6002

FRAME_WIDTH = 320
FRAME_HEIGHT = 240
CENTER_X = FRAME_WIDTH // 2

# 距离控制 (基于 bbox 面积而非高度, 更稳定)
TARGET_AREA = 40000 # *********************0期望跟随距离对应的 bbox 面积**********************
AREA_TOLERANCE = 8000        # 容忍范围: T ± 8000 内就停, 超出后退, 低于前进
TOO_CLOSE_AREA = 80000       # 紧急后退阈值 (面积超过此值强制后退)
MIN_AREA = 1500              # 最小面积过滤 (降低, 减少丢检)
KP_LINEAR = 0.00010          # V = 面积差 * KP_LINEAR
# 转向: 三区间控制 (同距离控制思路)
DEADZONE_CENTER = 25         # 中间区半宽 (像素): 人在 ±25px 内直走不转
FAR_ZONE_EDGE = 110          # 边缘区起点: 偏离超过此值视为"要出画面", 加快转向追回
TURN_GENTLE = 0.12           # 过渡区转向速度 (缓慢微调)
TURN_CATCHUP = 0.28          # 边缘区转向速度 (追回来, 但要防止 overshoot)
MAX_LINEAR_SPEED = 0.5 #**********************速度上线值*******************************
MAX_ANGULAR_SPEED = 0.75 #***********************转速上线值*****************************

# 状态机参数
LOST_GRACE_TIME = 0.8       # 丢失缓冲 (加长避免短暂丢检误触发单轮转)
SEARCH_TURN_SPEED = 0.4     # 搜索时身体旋转速度
SEARCH_TIMEOUT = 5.0        # 搜索超时后暂停一会

# 推断帧率 (用于时间估算)
EST_FPS = 25


class State(Enum):
    FOLLOW = 0   # 正常跟随
    LOST = 1     # 短暂丢失, 惯性维持
    SEARCH = 2   # 身体旋转搜索


# ================= 2. 控制算法 =================
def calculate_robot_command(xmin, ymin, xmax, ymax):
    """基于 bbox 面积和中心位置计算 V/W.
    正值 V = 前进, 正值 W = 左转 (协议约定)."""
    bbox_w = xmax - xmin
    bbox_h = ymax - ymin
    area = bbox_w * bbox_h
    cx = (xmin + xmax) / 2.0

    # 距离: 三区间控制
    # A 在 [T-TOL, T+TOL] → 停; A < T-TOL → 前进; A > T+TOL → 后退
    if area > TOO_CLOSE_AREA:
        v = (TARGET_AREA - area) * KP_LINEAR  # 紧急后退
    elif area > TARGET_AREA + AREA_TOLERANCE:
        v = (TARGET_AREA - area) * KP_LINEAR  # 有点近, 后退
    elif area < TARGET_AREA - AREA_TOLERANCE:
        v = (TARGET_AREA - area) * KP_LINEAR  # 有点远, 前进
    else:
        v = 0.0  # 在容忍范围内, 停

    error_x = CENTER_X - cx
    abs_error = abs(error_x)

    # 转向: 三区间控制 — 同距离控制思路
    # 中间区(±DEADZONE_CENTER): 直走; 过渡区: 缓慢微调; 边缘区: 加快追回
    if abs_error < DEADZONE_CENTER:
        w = 0.0  # 中间区: 不转, 直走
    elif abs_error < FAR_ZONE_EDGE:
        w = TURN_GENTLE if error_x > 0 else -TURN_GENTLE  # 过渡区: 缓慢微调
    else:
        w = TURN_CATCHUP if error_x > 0 else -TURN_CATCHUP  # 边缘区: 加快追回

    v = max(-MAX_LINEAR_SPEED, min(MAX_LINEAR_SPEED, v))
    w = max(-MAX_ANGULAR_SPEED, min(MAX_ANGULAR_SPEED, w))

    return v, w, area


# ================= 3. 调试可视化 =================
def draw_debug_ui(frame, state_idx, v, w, bbox_area, target_detected, best_xyxy, best_cx):
    """绘制调试叠加层: 三区界线 + 颜色编码 + 状态面板"""
    h, fw = frame.shape[:2]

    # --- 区界线 ---
    cv2.line(frame, (CENTER_X, 0), (CENTER_X, h), (0, 255, 0), 1)           # 中心线 绿
    for s in [-1, 1]:
        x_d = CENTER_X + s * DEADZONE_CENTER
        cv2.line(frame, (x_d, 0), (x_d, h), (180, 180, 180), 1)             # 死区界 灰
        x_f = CENTER_X + s * FAR_ZONE_EDGE
        cv2.line(frame, (x_f, 0), (x_f, h), (0, 140, 255), 1)               # 边缘界 橙

    # --- 区标签 (底部) ---
    cv2.putText(frame, "CENTER", (CENTER_X - 30, h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
    cv2.putText(frame, "TRANS", (CENTER_X + DEADZONE_CENTER + 4, h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (180, 180, 180), 1)
    cv2.putText(frame, "FAR", (CENTER_X + FAR_ZONE_EDGE + 4, h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 140, 255), 1)

    # --- bbox + 颜色编码 ---
    zone_name = "NONE"
    if target_detected and best_xyxy and best_cx is not None:
        abs_err = abs(CENTER_X - best_cx)
        if abs_err < DEADZONE_CENTER:
            color, zone_name = (0, 255, 0), "CENTER"
        elif abs_err < FAR_ZONE_EDGE:
            color, zone_name = (0, 255, 255), "TRANS"
        else:
            color, zone_name = (0, 0, 255), "FAR"
        cv2.rectangle(frame, (best_xyxy[0], best_xyxy[1]), (best_xyxy[2], best_xyxy[3]), color, 2)
        cv2.putText(frame, f"Z:{zone_name} E:{abs_err:.0f}px", (best_xyxy[0], best_xyxy[1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1)

    # --- 文字面板 ---
    state_names = {0: "FOLLOW", 1: "LOST", 2: "SEARCH"}
    cv2.putText(frame, f"State: {state_names.get(state_idx, '?')}", (5, 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
    cv2.putText(frame, f"V:{v:+.2f} W:{w:+.2f}", (5, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
    cv2.putText(frame, f"A:{bbox_area} T:{TARGET_AREA}", (5, 45),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)

    # 方向提示
    if v > 0.01:
        hint = ">> FWD >>"
    elif v < -0.01:
        hint = "<< BACK <<"
    else:
        hint = "-- STOP --"
    cv2.putText(frame, hint, (CENTER_X - 35, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)


# ================= 4. 主程序入口 =================
if __name__ == "__main__":
    print(">>> [系统] 纯视觉跟随已启动 (V2: 状态机 + 面积控制)")

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    udp_sock.sendto(json.dumps({"ORDER": 6}).encode(), (PI_IP, PI_CMD_PORT))
    print(">>> [系统] 已发送 ORDER:6 开启跟随")
    time.sleep(0.3)

    model = YOLO('yolo11n.pt')

    # ffmpeg 零缓冲 + 定期重连: 双重策略消除网络延迟
    import os as _os
    _os.environ.setdefault("OPENCV_FFMPEG_CAPTURE_OPTIONS", "max_delay;0;buffer_size;1024")
    try:
        cap = cv2.VideoCapture(VIDEO_URL, cv2.CAP_FFMPEG)
    except:
        cap = cv2.VideoCapture(VIDEO_URL)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    RECONNECT_EVERY = 40  # 每隔 N 帧强制重连, 彻底甩掉积压

    state = State.SEARCH
    last_seen_time = time.time()
    search_start_time = time.time()
    last_v, last_w = 0.0, 0.0
    last_payload = {"V": 0.0, "W": 0.0, "S": 0}
    last_bbox_area = 0
    last_bbox_xyxy = None
    last_bbox_cx = CENTER_X
    last_state_idx = State.SEARCH.value
    frame_count = 0
    INFER_EVERY_N = 3  # 每 N 帧推理一次

    while True:
        # 定期重连: 断开再连, 强制丢弃所有积压帧
        if frame_count > 0 and frame_count % RECONNECT_EVERY == 0:
            cap.release()
            try:
                cap = cv2.VideoCapture(VIDEO_URL, cv2.CAP_FFMPEG)
            except:
                cap = cv2.VideoCapture(VIDEO_URL)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            for _ in range(3):
                cap.grab()

        # 清空缓冲区: 持续抓帧直到缓冲区空, 只保留最后一帧 (消除网络延迟)
        drain_deadline = time.time() + 0.15  # 清缓冲时长 (越小越实时)
        grabbed = False
        while time.time() < drain_deadline:
            if cap.grab():
                grabbed = True
        if grabbed:
            ret, frame = cap.retrieve()
        else:
            ret, frame = False, None

        if not ret:
            time.sleep(0.01)
            continue

        # 统一缩放到配置分辨率, 确保面积计算一致
        frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

        frame_count += 1
        # 跳帧推理: 非推理帧复用上次结果, 大幅降低延迟
        if frame_count % INFER_EVERY_N != 0:
            udp_sock.sendto(json.dumps(last_payload).encode(), (PI_IP, PI_CMD_PORT))
            draw_debug_ui(frame, last_state_idx, last_payload['V'], last_payload['W'],
                          last_bbox_area, last_payload.get('S', 0) == 1, last_bbox_xyxy, last_bbox_cx)
            cv2.imshow("Wall-E Follow V2", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
            continue

        results = model(frame, classes=[0], stream=True, conf=0.35, verbose=False)

        cmd_v, cmd_w = 0.0, 0.0
        target_detected = False
        bbox_area = 0
        best_cx = CENTER_X
        best_xyxy = None

        # --- YOLO 目标提取 ---
        for res in results:
            if len(res.boxes) > 0:
                # 选面积最大的目标 (最近的人)
                box = sorted(
                    res.boxes,
                    key=lambda b: (b.xyxy[0][2] - b.xyxy[0][0]) * (b.xyxy[0][3] - b.xyxy[0][1]),
                    reverse=True
                )[0]
                xyxy = box.xyxy[0].cpu().numpy()
                xmin, ymin, xmax, ymax = xyxy
                area = (xmax - xmin) * (ymax - ymin)

                if area >= MIN_AREA:
                    target_detected = True
                    bbox_area = area
                    best_cx = (xmin + xmax) / 2.0
                    best_xyxy = (int(xmin), int(ymin), int(xmax), int(ymax))
                break

        # --- 状态机 ---
        if target_detected:
            last_seen_time = time.time()

            if state == State.SEARCH or state == State.LOST:
                state = State.FOLLOW

            if state == State.FOLLOW:
                cmd_v, cmd_w, bbox_area = calculate_robot_command(*best_xyxy)

            last_v, last_w = cmd_v, cmd_w
            last_bbox_area = bbox_area
            last_bbox_xyxy = best_xyxy
            last_bbox_cx = best_cx

        else:
            elapsed = time.time() - last_seen_time

            if elapsed < LOST_GRACE_TIME:
                # 短暂丢失: 减速惯性
                cmd_v, cmd_w = last_v * 0.25, last_w * 0.25
                state = State.LOST
            elif elapsed < 2.0:
                # 停止, 等待重捕获
                cmd_v, cmd_w = 0.0, 0.0
                state = State.LOST
            else:
                # 超过2秒: 身体旋转搜索
                state = State.SEARCH
                search_elapsed = time.time() - search_start_time
                if search_elapsed > SEARCH_TIMEOUT + 3.0:
                    # 避免一直转下去, 暂停恢复
                    search_start_time = time.time()
                    cmd_v, cmd_w = 0.0, 0.0
                elif search_elapsed > SEARCH_TIMEOUT:
                    # 搜索超时, 暂停
                    cmd_v, cmd_w = 0.0, 0.0
                else:
                    cmd_w = SEARCH_TURN_SPEED
                    cmd_v = 0.0

        # --- 构造 Payload ---
        payload = {
            "V": float(round(cmd_v, 2)),
            "W": float(round(cmd_w, 2)),
            "S": 1 if target_detected else 0
        }
        udp_sock.sendto(json.dumps(payload).encode(), (PI_IP, PI_CMD_PORT))
        last_payload = payload
        last_state_idx = state.value

        # --- UI 信息叠加 ---
        draw_debug_ui(frame, state.value, cmd_v, cmd_w, last_bbox_area,
                      target_detected, best_xyxy, best_cx)

        cv2.imshow("Wall-E Follow V2", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    udp_sock.close()
