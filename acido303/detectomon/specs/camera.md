## Camera Selection / Switch Camera

The web application must allow the user to switch between available cameras.

### Requirements

- The frontend must detect all available video input devices using the browser MediaDevices API.
- The application must show a button called "Switch Camera" or "Use Other Camera".
- When the user clicks the button:
  - The current camera stream must be stopped.
  - The next available camera must be selected.
  - A new stream must be opened using the selected camera `deviceId`.
  - Object detection must continue using the new camera feed.
- If only one camera is available, the button should be disabled or hidden.
- The selected camera should remain active until the user switches again or closes the page.

### Browser API

The implementation should use:

```js
navigator.mediaDevices.enumerateDevices()
navigator.mediaDevices.getUserMedia()