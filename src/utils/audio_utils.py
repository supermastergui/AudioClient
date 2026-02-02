#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from pyaudio import PyAudio

from src.model import DeviceInfo, HostApiInfo


def get_host_api_info() -> dict[str, HostApiInfo]:
    p = PyAudio()
    result = {}
    host_api_count = p.get_host_api_count()
    for i in range(host_api_count):
        host_info = HostApiInfo.model_validate(p.get_host_api_info_by_index(i))
        result[host_info.name] = host_info
    p.terminate()
    return result


def get_device_info(host_api: int) -> tuple[dict[str, DeviceInfo], dict[str, DeviceInfo]]:
    p = PyAudio()
    device_infos: list[DeviceInfo] = []
    device_count = p.get_device_count()
    for i in range(device_count):
        dev_info = DeviceInfo.model_validate(p.get_device_info_by_index(i))
        if dev_info.hostApi == host_api:
            device_infos.append(dev_info)
    p.terminate()
    input_devices: dict[str, DeviceInfo] = {}
    output_devices: dict[str, DeviceInfo] = {}
    for item in device_infos:
        if item.maxOutputChannels > 0:
            if item.name in output_devices:
                device = output_devices[item.name]
                if (device.defaultSampleRate < item.defaultSampleRate or
                        device.maxOutputChannels < item.maxOutputChannels):
                    output_devices[item.name] = item
            else:
                output_devices[item.name] = item
        if item.maxInputChannels > 0:
            if item.name in input_devices:
                device = input_devices[item.name]
                if (device.defaultSampleRate < item.defaultSampleRate or
                        device.maxInputChannels < item.maxInputChannels):
                    input_devices[item.name] = item
            else:
                input_devices[item.name] = item

    return input_devices, output_devices
