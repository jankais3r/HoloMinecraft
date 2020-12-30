# HoloMinecraft
Minecraft as a real-world hologram. No glasses required.

## Hardware Requirements
- [Looking Glass](https://lookingglassfactory.com) holographic display

## Software Requirements
### Server
- Minecraft Java Edition with Optifine
- Python 3 with the following modules `mss`, `pywin32`, `opencv-python`, `diff_match_patch`
- Windows (while this could be made to work on any OS, the window-identification part of the screen recording code is currently tailored for Windows)

### Client
- \[Optional\] [HoloPlay service](https://lookingglassfactory.com/software/holoplay-service) (HoloMinecraft is using a [patched version of HoloPlay.js](https://github.com/jankais3r/driverless-HoloPlay.js) to allow service-less operation)
- Web browser (If your client is an iOS device, use [this custom browser](https://github.com/jankais3r/iOS-LookingGlass))

![Demo](https://github.com/jankais3r/HoloMinecraft/blob/main/demo.gif)

See it in action [here](https://twitter.com/jankais3r/status/1343244779379961858) and [here](https://twitter.com/jankais3r/status/1343245360047804416).

## Setup
- If you plan on using HoloMinecraft in the service-less mode, get your calibration values at [here](https://eka.hn/calibration_test.html) and replace my values on [row 55](https://github.com/jankais3r/HoloMinecraft/blob/main/holominecraft.py#L55).
- If you are using a single computer as both server and client, you might have to reduce FPS on [row 40](https://github.com/jankais3r/HoloMinecraft/blob/main/holominecraft.py#L40), reduce the size of your Minecraft window, or both. I recommend using a PC as a server and an iPad as a client for best results.

## Steps
1) Put the DepthExtractor folder into your shaderpacks folder (e.g. `C:\Users\Username\AppData\Roaming\.minecraft\shaderpacks\`)
2) Enable the DepthExtractor shader in Minecraft (Options… -> Video Settings… -> Shaders…)
3) Run holominecraft.py
4) Open http://localhost:9090/holo.html in your browser, move the window to the Looking Glass display and enable Fullscreen.



