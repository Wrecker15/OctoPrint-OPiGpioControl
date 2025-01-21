/*
 * View model for OctoPrint-OPiGpioControl
 *
 * Author: Damian Wójcik & TTLC198
 * License: AGPLv3
 */
$(function () {
    function OPiGpioControlViewModel(parameters) {
        var self = this;
        self.settings = parameters[0];
        self.gpioButtons = ko.observableArray();
        self.gpioConfigurations = ko.observableArray();
        self.availableBoards = ko.observableArray(); // Observable array for available boards
        self.selectedBoard = ko.observable(); // Observable for the selected board

        self.onBeforeBinding = function () {
            self.gpioConfigurations(self.settings.settings.plugins.opigpiocontrol.gpio_configurations.slice(0));
            self.updateGpioButtons();
            self.fetchAvailableBoards(); // Fetch available boards on binding
        };

        self.onSettingsShown = function () {
            self.gpioConfigurations(self.settings.settings.plugins.opigpiocontrol.gpio_configurations.slice(0));
            self.updateIconPicker();
        };

        self.onSettingsHidden = function () {
            self.gpioConfigurations(self.settings.settings.plugins.opigpiocontrol.gpio_configurations.slice(0));
            self.updateGpioButtons();
        };

        self.onSettingsBeforeSave = function () {
            self.settings.settings.plugins.opigpiocontrol.gpio_configurations(self.gpioConfigurations.slice(0));
        };

        self.addGpioConfiguration = function () {
            self.gpioConfigurations.push({pin: 0, icon: "fas fa-plug", name: "", active_mode: "active_high", default_state: "default_off"});
            self.updateIconPicker();
        };

        self.removeGpioConfiguration = function (configuration) {
            self.gpioConfigurations.remove(configuration);
        };

        self.updateIconPicker = function () {
            $('.iconpicker').each(function (index, item) {
                $(item).iconpicker({
                    placement: "bottomLeft",
                    hideOnSelect: true,
                });
            });
        };

        self.updateGpioButtons = function () {
            self.gpioButtons(ko.toJS(self.gpioConfigurations).map(function (item) {
                return {
                    icon: item.icon,
                    name: item.name,
                    current_state: "unknown",
                }
            }));

            OctoPrint.simpleApiGet("opigpiocontrol").then(function (states) {
                self.gpioButtons().forEach(function (item, index) {
                    self.gpioButtons.replace(item, {
                        icon: item.icon,
                        name: item.name,
                        current_state: states[index],
                    });
                });
            });
        };

        self.turnGpioOn = function () {
            OctoPrint.simpleApiCommand("opigpiocontrol", "turnGpioOn", {id: self.gpioButtons.indexOf(this)}).then(function () {
                self.updateGpioButtons();
            });
        };

        self.turnGpioOff = function () {
            OctoPrint.simpleApiCommand("opigpiocontrol", "turnGpioOff", {id: self.gpioButtons.indexOf(this)}).then(function () {
                self.updateGpioButtons();
            });
        };

        self.fetchAvailableBoards = function () {
            OctoPrint.simpleApiCommand("opigpiocontrol", "fetch_boards", {}).done(function(response) {
                console.log("Fetched boards:", response); // Add this line for debugging
                self.availableBoards(response);
            }).fail(function() {
                console.error("Failed to fetch boards");
        });
    };
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: OPiGpioControlViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#settings_plugin_opigpiocontrol", "#sidebar_plugin_opigpiocontrol"]
    });
});
