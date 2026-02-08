# VoiceClient 工作原理与使用方法

## 一、概述

`VoiceClient` 是语音业务的入口类，负责：

- **网络**：通过 TCP 发送信令、UDP 发送/接收语音包，与语音服务器通信
- **音频**：管理麦克风采集、Opus 编码、双路输出（耳机/扬声器）与播放
- **逻辑**：维护本机「发射机」（Transmitter）列表与频率索引，将收到的语音按**频率**路由到对应通道播放

应用层（管制窗、飞行员窗、连接窗等）只与 `VoiceClient` 和 `Transmitter` 交互，不直接碰网络或音频设备。

---

## 二、工作原理

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        VoiceClient                               │
├─────────────────────────────────────────────────────────────────┤
│  client_info         本机用户/呼号/JWT 等                         │
│  _transmitters       id → Transmitter（本机所有逻辑电台）          │
│  _transmitters_by_   frequency → Transmitter（收包时 O(1) 查找）  │
│  frequency                                                       │
│  _current_           当前用于发送的 transmitter id（PTT 时用）     │
│  transmitter_id                                                   │
├──────────────┬──────────────────────┬────────────────────────────┤
│ NetworkHandler │     AudioHandler     │  信号 (signals)             │
│ TCP 信令      │  输入流 + 双路混合输出  │  connection_state_changed   │
│ UDP 语音收发   │  PTT 提示音 / 冲突音   │  voice_data_received 等     │
└──────────────┴──────────────────────┴────────────────────────────┘
```

- **NetworkHandler**：连接后发 JWT，TCP 按行解析 `ControlMessage`（如 SWITCH、Welcome、DISCONNECT），UDP 解析 `VoicePacket` 并通过
  `signals.voice_data_received` 交给 VoiceClient。
- **AudioHandler**：麦克风 → Opus 编码 → 通过 `on_encoded_audio` 回调交给 VoiceClient 发送；接收侧由 VoiceClient 根据频率找到对应
  Transmitter，再调用 `AudioHandler.play_encoded_audio` 按 `transmitter.output_target` 送入耳机或扬声器混合流。

### 2.2 连接与就绪状态

1. **连接**：`connect_to_server(host, tcp_port, udp_port)` 使用 `client_info.jwt_token` 建立 TCP + UDP，并发送 JWT 验证。
2. **就绪**：服务端返回带 `Welcome` 的 MESSAGE 后，VoiceClient 解析呼号、启动音频（`_audio.start()`），并置
   `connection_state = READY`。只有 **READY** 且 **client_info.client_valid** 时 `client_ready` 为 True。
3. **断开**：`disconnect_from_server()` 或收到 DISCONNECT 会清理 transmitters、停止音频并断开网络。

### 2.3 Transmitter 与频率

- **Transmitter** 表示一个「逻辑电台」，包含：
    - `id`：本机内唯一
    - `frequency`：频率（如 122800 表示 122.800）
    - `send_flag` / `receive_flag`：是否允许发/收
    - `volume`：播放音量
    - `output_target`：`"headphone"` 或 `"speaker"`，决定从哪路设备出声

- **频率索引**：`_transmitters_by_frequency` 由 `_transmitters` 在添加/更新 transmitter 时重建，满足「同用户同频仅一台」的后端约定，收包时用
  `packet.frequency` 做 O(1) 查找。

### 2.4 发送语音（PTT）

1. 用户按住 PTT → 通过信号设置 `_sending = True`，并指定当前发射通道（见下文的「当前发送通道」）。
2. `AudioHandler` 的输入流在 PTT 激活时采集麦克风并编码，通过 **on_encoded_audio** 回调到 VoiceClient 的
   `_send_voice_data`。
3. `_send_voice_data` 仅在 `client_ready` 且 `_current_transmitter_id != -1` 时工作，用当前 transmitter 的 `id`、
   `frequency` 和 `client_info.cid/callsign` 组包，经 **NetworkHandler** 用 UDP 发出。

### 2.5 接收语音与冲突判定

1. **NetworkHandler** 收到 UDP 语音包后解析为 `VoicePacket`（含 cid、transmitter、frequency、callsign、data），通过 *
   *voice_data_received** 传给 VoiceClient。
2. **注意**：服务端转发的是发送方原始数据，`packet.transmitter` 是**发送方**的 transmitter id，不能用来查本机。本机用 *
   *packet.frequency** 在 `_transmitters_by_frequency` 中查找对应的 **本机 Transmitter**。
3. **冲突**：若「本机正在发送」或「该频率在约 5 帧时间内收到不同 callsign 的包」，则视为冲突，播放冲突音（可配置音量）；否则正常播放语音。
4. 播放时根据该 Transmitter 的 `receive_flag`、`volume`、`output_target` 由 AudioHandler 送入对应混合流（耳机或扬声器）。

### 2.6 信令（SWITCH）

当 UI 改变某个 Transmitter 的频率或收发状态时，应调用 `update_transmitter(transmitter)`：

- 会重建频率索引并发送 **SWITCH** 信令（MessageType.SWITCH），携带 `frequency` 与 `receive_flag`（1/0），使服务端同步本机该通道的守听状态。
- 若该 transmitter 的 `send_flag` 为 True，会同时更新 `_current_transmitter_id` 并发出 **update_current_frequency** 信号，供
  UI 显示当前发射频率。

---

## 三、使用方法

### 3.1 创建与注入

在主窗口或应用初始化处创建**一个** VoiceClient，并注入到需要语音/连接的界面：

```python
from src.core import VoiceClient
from src.signal import AudioClientSignals

signals = AudioClientSignals()
voice_client = VoiceClient(signals)

# 登录成功后写入身份信息
voice_client.update_client_info(login_data)

# 连接、管制窗、飞行员窗等均持有同一 voice_client 实例
connect_window = ConnectWindow(signals, voice_client)
controller_window = ControllerWindow(signals, voice_client)
client_window = ClientWindow(signals, voice_client)
```

### 3.2 连接与断开

- **连接**：在连接界面取得 `host, tcp_port, udp_port` 后调用  
  `voice_client.connect_to_server(host, tcp_port, udp_port)`  
  需在登录成功后调用，以便 `client_info.jwt_token` 已存在。
- **断开**：  
  `voice_client.disconnect_from_server()`  
  会清理 transmitters、停止音频并断开 TCP/UDP。

### 3.3 监听连接状态与错误

- 连接状态：  
  `voice_client.signals.connection_state_changed.connect(your_slot)`  
  参数为 `ConnectionState`（如 DISCONNECTED / CONNECTING / CONNECTED / READY）。
- 是否可发话/收话：  
  `if voice_client.client_ready: ...`
- 错误：  
  `voice_client.signals.error_occurred.connect(your_slot)`  
  参数为错误信息字符串。

### 3.4 添加与管理 Transmitter

- **添加**：创建 `Transmitter(frequency, transmitter_id, ...)` 后：  
  `voice_client.add_transmitter(transmitter)`  
  会加入本机列表、在 AudioHandler 中注册，并若频率非 0 会发一次 SWITCH。
- **改频率/收发/音量/输出设备**：修改 `transmitter` 的对应属性后：  
  `voice_client.update_transmitter(transmitter)`  
  仅在 `client_ready` 时会发 SWITCH 并更新当前发送通道（若 send_flag 为 True）。
- **仅改输出设备（耳机/扬声器）**：  
  `voice_client.set_transmitter_output_target(transmitter)`  
  调用前请先把 `transmitter.output_target` 设为 `"headphone"` 或 `"speaker"`。

典型用法（管制端多通道）：

```python
# 创建
main = Transmitter(122800, 0, tx=True, rx=True)
unicom = Transmitter(122800, 1, tx=False, rx=True)
# ...
voice_client.add_transmitter(main)
voice_client.add_transmitter(unicom)
# 用户切换主频或收发时
main.frequency = 121500
main.receive_flag = True
voice_client.update_transmitter(main)
```

飞行员端（COM1/COM2）同理，只是通常两个 Transmitter 固定存在，只改频率或输出目标。

### 3.5 当前发送通道（PTT 用）

- 发送语音时，VoiceClient 使用 **当前发送通道** `_current_transmitter_id` 对应的 Transmitter 的 id、frequency、callsign 组包。
- 当某个 Transmitter 的 `send_flag` 为 True 且调用 `update_transmitter(transmitter)` 时，会自动把该 transmitter
  设为当前发送通道，并发出 `update_current_frequency`。
- 因此 UI 应在「用户选择要发射的通道」时，将该通道的 `send_flag` 设为 True、其余为 False，然后对当前选中的 transmitter 调用
  `update_transmitter`。

### 3.6 文本消息（可选）

已就绪时：  
`voice_client.send_text_message(target, message)`  
会通过信令发送文本消息（具体格式由服务端约定）。

### 3.7 音频与设备

- 实际采集、编解码、播放由 **AudioHandler** 完成，通过只读属性访问：  
  `voice_client.audio`  
  例如设备测试、冲突音试听等若由配置窗通过 signals 与 AudioHandler 交互，无需直接操作 `voice_client.audio`，除非你要扩展功能。
- 设备切换、PTT 提示音、冲突音音量等均通过 **AudioClientSignals** 与配置/UI 联动，VoiceClient 内部已连接好。

### 3.8 关闭应用

在应用退出前：  
`voice_client.shutdown()`  
会断开网络并关闭音频资源。

---

## 四、相关类型与信号速查

| 类型/信号                      | 说明                                                  |
|----------------------------|-----------------------------------------------------|
| `Transmitter`              | 频率、id、send_flag、receive_flag、volume、output_target   |
| `ConnectionState`          | DISCONNECTED / CONNECTING / CONNECTED / READY 等     |
| `VoicePacket`              | cid, transmitter（发送方 id）, frequency, callsign, data |
| `connection_state_changed` | 连接状态变化                                              |
| `voice_data_received`      | 收到一条语音包（已在 VoiceClient 内处理，一般不需再连）                  |
| `voice_data_sent`          | 本机发出一条语音（可用于 UI 指示）                                 |
| `update_current_frequency` | 当前发射频率变化（int，如 122800）                              |
| `error_occurred`           | 错误信息（str）                                           |

---

## 五、小结

- **VoiceClient** = 网络（信令 + 语音包）+ 音频路由 + 本机 Transmitter/频率管理。
- **收包**：用 `packet.frequency` 查本机 Transmitter，再按 `receive_flag`/`volume`/`output_target` 播放到耳机或扬声器。
- **发包**：PTT 时由当前发送通道（`_current_transmitter_id`）对应的 Transmitter 提供 id/frequency/callsign 组包发送。
- **使用**：创建并注入到各窗口，用 `add_transmitter` / `update_transmitter` / `set_transmitter_output_target` 管理通道，用
  `connect_to_server` / `disconnect_from_server` 控制连接，通过 `signals` 监听状态与错误即可。
