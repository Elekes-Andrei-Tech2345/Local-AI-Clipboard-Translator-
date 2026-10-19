# Local AI Clipboard Translator

A lightweight, multi-threaded desktop utility that monitors the system clipboard to capture text data streams (such as live hooks from textractor) and executes real-time translations via a local LLM environment.

## Key Features

* Multi-Threaded Architecture: Separates the background clipboard monitoring from the frontend UI rendering loop, preventing UI freezes during high-frequency data inputs.
* Local Backend Integration: Formats captured text strings alongside simple system instructions and ships payload to local API endpoints (compatible with koboldcpp).
* Input Filters: Utilizes string filters to intercept and discard certain phrases or game menu commands, preventing redundant translations.
* Custom UI: Built on a customized tkinter layout designed to match the targeted aesthetic of game ui for native visual integration.

## Technical Architecture & Dependencies

The project is written completely in Python and leverages core built-in and optimized packages to handle low-latency system integration:
* tkinter - Lightweight desktop window management and interface customization.
* openai - Client SDK configured for localized endpoint communication via loopback ports.
* threading - Asynchronous background pipeline execution for state and input scanning.
* pyperclip - Low-level cross-platform clipboard polling hook abstraction.
