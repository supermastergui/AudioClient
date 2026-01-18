#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from pyaudio import PyAudio


def get_host_api_info() -> dict[str, int]:
    p = PyAudio()
    result = {}
    host_api_count = p.get_host_api_count()
    for i in range(host_api_count):
        host_info = p.get_host_api_info_by_index(i)
        result[host_info["name"]] = i
    p.terminate()
    return result


def get_device_info(host_api: int) -> tuple[dict[str, int], dict[str, int]]:
    p = PyAudio()
    device_infos = []
    device_count = p.get_device_count()
    for i in range(device_count):
        dev_info = p.get_device_info_by_index(i)
        if dev_info['hostApi'] == host_api:
            try:
                dev_info["name"] = dev_info["name"].encode("GBK").decode("utf8")
            except UnicodeEncodeError:
                pass
            except UnicodeDecodeError:
                pass
            device_infos.append(dev_info)
    p.terminate()
    input_devices = {}
    output_devices = {}
    for item in device_infos:
        if item["maxOutputChannels"] > 0:
            if item["name"] in output_devices:
                device = output_devices[item["name"]]
                if (device["defaultSampleRate"] < item["defaultSampleRate"] or
                        device["maxOutputChannels"] < item["maxOutputChannels"]):
                    output_devices[item["name"]] = item
            else:
                output_devices[item["name"]] = item
        if item["maxInputChannels"] > 0:
            if item["name"] in input_devices:
                device = input_devices[item["name"]]
                if (device["defaultSampleRate"] < item["defaultSampleRate"] or
                        device["maxInputChannels"] < item["maxInputChannels"]):
                    input_devices[item["name"]] = item
            else:
                input_devices[item["name"]] = item

    for item in input_devices.keys():
        input_devices[item] = input_devices[item]["index"]

    for item in output_devices.keys():
        output_devices[item] = output_devices[item]["index"]

    return input_devices, output_devices
