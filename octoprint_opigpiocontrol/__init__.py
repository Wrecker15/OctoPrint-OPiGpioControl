# coding=utf-8
from __future__ import absolute_import, print_function
from octoprint.server import user_permission

import octoprint.plugin
import flask
import OPi.GPIO as GPIO
import orangepi.zero2 as orangepi

class OPiGpioControlPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.SimpleApiPlugin,
    octoprint.plugin.RestartNeedingPlugin,
):
    mode = None

    def on_startup(self, *args, **kwargs):
        GPIO.setwarnings(False)
        GPIO.setmode(orangepi.BOARD)

        self._logger.info("Setup GPIO mode: {}".format(orangepi.BOARD))

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
        return dict(gpio_configurations=[])

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
        return dict(turnGpioOn=["id"], turnGpioOff=["id"], getGpioState=["id"])

    def on_api_command(self, command, data):
        if not user_permission.can():
            return flask.make_response("Insufficient rights", 403)

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
                user="Wrecker15",
                repo="OctoPrint-OPiGpioControl",
                current=self._plugin_version,
                stable_branch=dict(
                    name="Stable",
                    branch="OPi-Zero2",
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
    # Orange Pi Zero 2 physical board pin to GPIO pin
    PIN_MAPPINGS = {
        3:    229,   # PH5/I2C3_SDA
        5:    228,   # PH4/I2C3_SCK
        7:    73,    # PC9
        8:    226,   # PH2/UART5_TX
        10:   227,   # PH3/UART5_RX
        11:   70,    # PC6
        12:   75,    # PC11
        13:   69,    # PC5
        15:   72,    # PC8
        16:   79,    # PC15
        18:   78,    # PC14
        19:   231,   # PH7,SPI1_MOSI
        21:   232,   # PH8,SPI1_MISO
        22:   71,    # PC7
        23:   230,   # PH6,SPI1_CLK
        24:   233,   # PH9,SPI1_CS
        26:   74,    # PC10
    }

    def get_pin_number(self, pin):
        if pin in self.PIN_MAPPINGS_PC:
            return self.PIN_MAPPINGS_PC[pin]

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
