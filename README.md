# AITPI
Arbitrary Input for Terminal or a PI, or Aitpi (pronounced 'eight pi')

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
{
    "type0": {
        "commandName0": {
            "mechanism": "button",
            "id": "4"
        },
        "commandName1": {
            "mechanism": "button",
            "id": "5"
        }
    },
    "type1": {
        "commandName2": {
            "mechanism": "encoder",
            "id": "1"
        }
    }
}
```
- The first layer of json define what 'type' each command is. You can use this to sort your commands in a meaningful way.
    - NOTE: Currently, you need a single type layer and cannot have more. This will be remedied in the future to allow 'foldered' types
- Each command is listed with a name, and a corrosponding dictionary.
    - Each command name must be unique regardless of type (this will be remedied once foldered types are implemented)
    - Each command must have a 'mechanism' and 'id' attribute
        - 'mechanism' lets Aitpi know what type of input this can be connected to
            - Valid mechanisms: 'encoder', 'button'
        - 'id' is the message id that the command events will be sent over
            - Valid ids: Any positive int, negative ints are reserved for Aitpi and could produce bad side effects

## Input list
The list of all 'input units' that your system uses
```
[
    {
        "name": "Button0",
        "type": "button",
        "mechanism": "gpio",
        "trigger": "5",
        "reg_link": "NAME1"
    },
    {
        "name": "Encoder0",
        "type": "encoder",
        "mechanism": "gpio",
        "trigger": "5",
        "reg_link": "NAME1"
    }
]
```
- This is an array of depth 1, with all your 'input units' listed as dictionaries inside
    - "name": specifies the name of the input unit
        - Valid names: Any string, must be unique among all input units
    - "type": specifies what type of input this unit is
        - Valid types: 'button', 'encoder'
    - "mechanism": This tells Aitpi by what mechanism the input will be watched
        - Valid mechanisms: 'key_interrupt', 'key_input', 'gpio'
            - key_interrupt: Uses [pynput](https://pypi.org/project/pynput/) to set interrupts on your keyboard itself
            - key_input: Manual in-code input through the function 'aitpi.takeInput'
            - gpio: Raspberry pi GPIO input, all input units are assumed to be active high
    - "trigger": The key string or gpio number that will trigger input
        - Valid triggers: Any string, or any valid unused gpio number on a raspberry pi
            - Note strings of more than one char will not work with key_interrupt (pynput)
    - "reg_link": This corrosponds to a command from the command registry and will determine what message is sent to your user program

## Foldered Commands
Foldered commands allows you to consider all the files in a folder as a 'command' in the registry.
This uses the [watchdog](https://pythonhosted.org/watchdog/) python package to monitor folders and update on the fly.
All commands added will be deleted and reloaded upon program startup.
```
[
    {
        "path": "/path/to/your/folder",
        "type": "<registry_type>",
        "id": "1",
        "mechanism": "button"
    },
    {
        "path": "/another/path",
        "type": "<registry_type>",
        "id": "2",
        "mechanism": "encoder"
    }
]
```
- This is an array of depth 1 that lists all the folders you want to add
    - "path": Specifies the folder that will be watched
        - Valid paths: Any valid folder on your system
    - "type": This will tell Aitpi where to insert the commands from the folder into your command registry
        - Valid types: Any string
    - "id": When a command is added from the folder, this id will be the command registry 'id' value
        - Valid ids: Any positive int, negative ints are reserved for Aitpi and could produce bad side effects
    - "mechanism": When a command is added from the folder, this mechanism will be the command registry 'mechanism' value
