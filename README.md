# AITPI
Arbitrary Input for Terminal or a PI

# Goal
The goal of this project is to provide a simple, but arbitrary, input
mechanism for use with a raspberry pi, or a terminal keyboard.

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
To configure your setup, see the two example json files:
- [example_input.json](./example_input.json)
- [example_command_registry.json](./example_registry.json)