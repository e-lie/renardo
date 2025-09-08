


# Reaper

- [ ] Try to reproduce your setup using the 

# Language

- [ ] Debug Point in Time
  - [ ] add logging :)))

# Clock

- [ ] add logging
- [ ] clean all sync mechanism
- [ ] refacto/comment for better clarity
- [ ] add AbletonLink sync

# Webclient

- [ ] improve the top menu design especially responsiveness
- [ ] redesign a new editor page
  - [ ] use a PythonTextBuffer subclass for Renardo code (and JSTextBuffer for Strudel, Hydra, P5integration)
  - [ ] create a customizable editor layout
    - [ ] editor (center) - top menu - up left - bottom left - up bottom right - bottom left and right panes
    - [ ] resizable
    - [ ] top right button that open a big modal for layout customization
    - [ ] system logs modal also with a top right button
    - [ ] responsiveness : only editor with collapsible panes
  - [ ] add
  - [ ] multiwindow mode for electron only (less prio)

# Electron packaging

- [ ] avoid pip install at app launching if already done (take a long time to launch the window each time)
- [ ] launch electron window quickly with an integrated waiting/diagnosis page that is nice and clear rather than waiting for flask process launch
  - [ ] maybe logging file for flask launch and waiting page display this log file...
- [ ] improve the windows installer look and feel
- [ ] hide electron menu