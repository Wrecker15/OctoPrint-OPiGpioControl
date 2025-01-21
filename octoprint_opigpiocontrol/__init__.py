# coding=utf-8
from __future__ import absolute_import, print_function
from octoprint.server import user_permission

import octoprint.plugin
import flask
import json
import OPi.GPIO as GPIO
import importlib
import os

class OPiGpioControlPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.SimpleApiPlugin,
    octoprint.plugin.RestartNeedingPlugin,
):
    mode = None
    board_module = None

    def on_startup(self, *args, **kwargs):
        GPIO.setwarnings(False)
        selected_board = self._settings.get(["selected_board"])
        self.board_module = importlib.import_module(f"orangepi.{selected_board}")
        GPIO.setmode(self.board_module.BOARD)

        self._logger.info("Setup GPIO mode: {}".format(self.board_module.BOARD))

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=True),
            dict(
                type="sidebar",
                custom_bindings=False,
                template="opigpiocontrol_sidebar.jinja2",
                icon="sliders",
            ),
        ]

    def get_assets(self):
        return dict(
            js=["js/opigpiocontrol.js", "js/fontawesome-iconpicker.min.js"],
            css=["css/opigpiocontrol.css", "css/fontawesome-iconpicker.min.css"],
        )

    def get_settings_defaults(self):
        return dict(
            gpio_configurations=[],
            selected_board="pc",  # Default board
        )

    def on_settings_save(self, data):
        for configuration in self._settings.get(["gpio_configurations"]):
            self._logger.info(
                "Cleaned GPIO {}: {},{} ({})".format(
                    configuration["pin"],
                    configuration["active_mode"],
                    configuration["default_state"],
                    configuration["name"],
                )
            )

            pin = self.get_pin_number(configuration["pin"])

            if pin > 0:
                GPIO.cleanup(pin)

        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

        for configuration in self._settings.get(["gpio_configurations"]):
            self._logger.info(
                "Reconfigured GPIO {}: {},{} ({})".format(
                    configuration["pin"],
                    configuration["active_mode"],
                    configuration["default_state"],
                    configuration["name"],
                )
            )

            pin = self.get_pin_number(configuration["pin"])

            if pin > 0:
                self.init_pin(pin)
                if configuration["active_mode"] == "active_low":
                    if configuration["default_state"] == "default_on":
                        GPIO.output(pin, GPIO.LOW)
                    elif configuration["default_state"] == "default_off":
                        GPIO.output(pin, GPIO.HIGH)
                elif configuration["active_mode"] == "active_high":
                    if configuration["default_state"] == "default_on":
                        GPIO.output(pin, GPIO.HIGH)
                    elif configuration["default_state"] == "default_off":
                        GPIO.output(pin, GPIO.LOW)

    def on_after_startup(self):
        for configuration in self._settings.get(["gpio_configurations"]):
            self._logger.info(
                "Configured GPIO {}: {},{} ({})".format(
                    configuration["pin"],
                    configuration["active_mode"],
                    configuration["default_state"],
                    configuration["name"],
                )
            )

            pin = self.get_pin_number(configuration["pin"])

            if pin != -1:
                self.init_pin(pin)
                if configuration["active_mode"] == "active_low":
                    if configuration["default_state"] == "default_on":
                        GPIO.output(pin, GPIO.LOW)
                    elif configuration["default_state"] == "default_off":
                        GPIO.output(pin, GPIO.HIGH)
                elif configuration["active_mode"] == "active_high":
                    if configuration["default_state"] == "default_on":
                        GPIO.output(pin, GPIO.HIGH)
                    elif configuration["default_state"] == "default_off":
                        GPIO.output(pin, GPIO.LOW)

    def get_api_commands(self):
        return dict(
            turnGpioOn=["id"], turnGpioOff=["id"], getGpioState=["id"],
            fetch_boards=[]
        )

    def on_api_command(self, command, data):
        if not user_permission.can():
            return flask.make_response("Insufficient rights", 403)
    
        if command == "fetch_boards":
            boards_path = os.path.join(os.path.dirname(__file__), 'path_to_OPiGPIO_directory', 'orangepi')
            boards = []
            for file_name in os.listdir(boards_path):
                if file_name.endswith('.py'):
                    boards.append(file_name.replace('.py', ''))
            return flask.jsonify(boards)
  

        configuration = self._settings.get(["gpio_configurations"])[int(data["id"])]
        pin = self.get_pin_number(configuration["pin"])
        
        if command == "getGpioState":
            if pin < 0:
                return flask.jsonify("")
            elif configuration["active_mode"] == "active_low":
                return flask.jsonify("off" if GPIO.input(pin) else "on")
            elif configuration["active_mode"] == "active_high":
                return flask.jsonify("on" if GPIO.input(pin) else "off")
        elif command == "turnGpioOn":
            if pin > 0:
                self._logger.info("Turned on GPIO {}".format(configuration["pin"]))
                if configuration["active_mode"] == "active_low":
                    GPIO.output(pin, GPIO.LOW)
                elif configuration["active_mode"] == "active_high":
                    GPIO.output(pin, GPIO.HIGH)
        elif command == "turnGpioOff":
            if pin > 0:
                self._logger.info("Turned off GPIO {}".format(configuration["pin"]))
                if configuration["active_mode"] == "active_low":
                    GPIO.output(pin, GPIO.HIGH)
                elif configuration["active_mode"] == "active_high":
                    GPIO.output(pin, GPIO.LOW)

    def on_api_get(self, request):
        states = []

        for configuration in self._settings.get(["gpio_configurations"]):
            pin = self.get_pin_number(configuration["pin"])
            if pin < 0:
                states.append("")
            elif configuration["active_mode"] == "active_low":
                states.append("off" if GPIO.input(pin) else "on")
            elif configuration["active_mode"] == "active_high":
                states.append("on" if GPIO.input(pin) else "off")

        return flask.jsonify(states)

    def get_update_information(self):
        return dict(
            opigpiocontrol=dict(
                displayName="OPi GPIO Control",
                displayVersion=self._plugin_version,
                type="github_release",
                user="TTLC198",
                repo="OctoPrint-OPiGpioControl",
                current=self._plugin_version,
                stable_branch=dict(
                    name="Stable",
                    branch="master",
                    comittish=["master"],
                ),
                prerelease_branches=[
                    dict(
                        name="Prerelease",
                        branch="development",
                        comittish=["development", "master"],
                    )
                ],
                pip="https://github.com/TTLC198/OctoPrint-OPiGpioControl/archive/{target_version}.zip",
            )
        )

    def get_pin_number(self, pin):
        if pin in self.board_module.BOARD:
            return self.board_module.BOARD[pin]
        return -1

    def init_pin(self, pin):
        try:
            GPIO.setup(pin, GPIO.OUT)
        except RuntimeError:
            GPIO.cleanup(pin)
            GPIO.setup(pin, GPIO.OUT)


__plugin_name__ = "OPi GPIO Control"
__plugin_pythoncompat__ = ">=2.7,<4"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = OPiGpioControlPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
