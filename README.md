# AITPI
Arbitrary Input for Terminal or a Pi, or Aitpi (pronounced 'eight pi')

# Goal
The goal of this project is to provide a simple, but arbitrary, input
mechanism for use with a raspberry pi, or a terminal keyboard (maybe more SBCs in the future?!).

This program can be configured with two simple json files.

# Supported
The project supports:
- Simple 'buttons'
    - '1 to 1' gpio to button setup on a raspberry pi
    - Non interrupt based key input
    - Interrupt based key input (using pynput)
- Encoders
    - '2 to 1' gpio to encoder setup on a raspberry pi
    - Non interrupt based 2 to 1 key input
    - Interrupt based 2 to 1 key input (using pynput)

# Examples
To configure your setup, you can create up to three types of json files:

## Command Registry:
A registry of commands that will interact directly with your user program
```
[
    {
        "type": "normal",
        "input_type": "button",
        "id": "1",
        "name": "command0"
    },
    {
        "id": "1",
        "input_type": "button",
        "path": "../temp/",
        "type": "presets",
        "name": "howdy"
    },
    {
        "id": "1",
        "input_type": "button",
        "path": "../temp/",
        "type": "presets",
        "name": "test"
    },
    {
        "id": "1",
        "input_type": "button",
        "path": "../temp/",
        "type": "presets",
        "name": "another.txt"
    }
]
```
- name: A UNIQUE identifier that is presented.
- id: The message id sent with each command
- input_type: The abstract functional representation i.e. (for now) a button or an encoder
- type: Category for each command. Must be defined, but is only used to sort commands usefully
- path: Only used for foldered commands. Tells the file path of the represented file.

## Input list
The list of all 'input units' that your system uses
```
[
    {
        "name": "Button0",
        "type": "button",
        "mechanism": "rpi_gpio",
        "trigger": "5",
        "reg_link": "commandName0"
    },
    {
        "name": "Encoder0",
        "type": "encoder",
        "mechanism": "rpi_gpio",
        "left_trigger": "17",
        "right_trigger": "24",
        "reg_link": "commandName2"
    }
]
```
- This is an array of depth 1, with all your 'input units' listed as dictionaries inside
    - "name": specifies the name of the input unit
        - Valid names: Any string, must be unique among all input units
    - "type": specifies what type of input this unit is
        - Valid types: 'button', 'encoder'
    - "mechanism": This tells Aitpi by what mechanism the input will be watched
        - Valid mechanisms: 'key_interrupt', 'key_input', 'rpi_gpio'
            - key_interrupt: Uses [pynput](https://pypi.org/project/pynput/) to set interrupts on your keyboard itself
            - key_input: Manual in-code input through the function 'aitpi.takeInput'
            - rpi_gpio: Raspberry pi GPIO input, all input units are assumed to be active low
    - "trigger": The key string or gpio number that will trigger input for a button
        - NOTE: This is only needed if 'type' equals 'button'
        - Valid triggers: Any string, or any valid unused gpio number on a raspberry pi
            - Note strings of more than one char will not work with key_interrupt (pynput)
    - "left_trigger" and "right_trigger: The key string or gpio numbers that will act as a left or right for an encoder
        - NOTE: These are only needed if 'type' equals 'encoder'
        - Valid left_triggers and right_triggers: Any string, or any valid unused gpio number on a raspberry pi
            - Note strings of more than one char will not work with key_interrupt (pynput)
    - "reg_link": This corrosponds to a command from the command registry and will determine what message is sent to your user program

## Foldered Commands
Foldered commands allows you to consider all the files in a folder as a 'command' in the registry.
This uses the [watchdog](https://pythonhosted.org/watchdog/) python package to monitor folders and update on the fly.
All commands added will be deleted and reloaded upon program startup.
```
[
    {
        "name": "Folder0",
        "path": "/path/to/your/folder",
        "type": "<registry_type>",
        "id": "3",
        "input_type": "button"
    },
    {
        "name": "Folder1",
        "path": "/another/path",
        "type": "<registry_type>",
        "id": "4",
        "input_type": "encoder"
    }
]
```
- This is an array of depth 1 that lists all the folders you want to add
    - "name": Gives a name that you can use to access the json using 'getFolderedCommands'
        - Valid names: Any string
    - "path": Specifies the folder that will be watched
        - Valid paths: Any valid folder on your system
    - "type": This will tell Aitpi where to insert the commands from the folder into your command registry
        - Valid types: Any string
    - "id": When a command is added from the folder, this id will be the command registry 'id' value
        - Valid ids: Any positive int, negative ints are reserved for Aitpi and could produce bad side effects
    - "input_type": When a command is added from the folder, this directly corrosponds to the command registry's 'input_type'


# Example usage:
```python

# import the base aitpi
import aitpi
from aitpi import router

# In order to receive messages can either make an object with a consume(message) function
# or just provide a function `def consume(message)`
class Watcher():
    def consume(self, message):
        print("Got command: %s" % message.name)
        print("On event: %s" % message.event)
        print("All attributes: %s" % message.attributes)

watcher = Watcher()

# Here we add a consumer that will receive commands with ids 0,1,2,3,4, these ids are the same
# as defined in your registry json file
router.addConsumer([0,1,2,3,4], watcher)

# We must first initialize our command registry before we can start getting input
aitpi.addRegistry("<path_to_json>/command_reg.json", "<path_to_json>/foldered_commands.json")

# We can add multiple registries, and do not need the foldered commands
aitpi.addRegistry("<path_to_json>/another_reg.json")

# Once we initialize our system, all interrupt based commands can be sent imediately.
# Therefore, make sure you are ready to handle any input in your functions before calling this.
aitpi.initInput("<path_to_json>/example_input.json")

# For synchronous input (not interrupt based) using the 'key_input' input mechanism is desireable
# You can setup a custom progromatic form of input using this (If it is good enough, add it to AITPI!)
while (True):
    aitpi.takeInput(input())
```