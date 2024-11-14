


### Problems to solve

- [ ] use volume adjustement to get rid of useless sends
- [ ] create the project from scratch
- [ ] crash of reapy connection (when python is killed for example)
- [ ] update param queue saturation (redesign queue)
- [ ] handle presets and utility function as modules/assets
- [ ] handle loading renardo_reaper conditionnally with try
- [ ] create cleaner extensibility of renardo by creating hooks where necessary (in Player and Clock etc)

### Improvement features ideas

- initiate project from scratch them add a function to save it as project template to reload it quicker
    - a `build_and_save_as_tpl` function/class that takes a series of actions, start a project from scratch, apply the action and save the result automatically would be nice...

- look at the specifics of vital params and create a class with :
    - better aliases for usefull params
    - handling of osc activation, filter activation, fxs activation
    - try to configure a preset from scratch ?
    - save current result as new fx template
    - create a very general wavetable stacking several wavetables...
    - try to use conversion from real values for envelopes, fx params, octaves etc

- same for surge xt which is lighter
- try to do kicks with surge...



### Redesign queue

- look at the implementation of inside_reaper context
- create a new mode of general execution "inside reaper" that uses a thread and automatically batches the codelines to execute