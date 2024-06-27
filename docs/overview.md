# Pytheas Overview

Pytheas is an agent-based model to study seafaring in ancient times. It is primarily used within the Maritime Encounters project, where we are studying the travels of Nordic populations during the Bronze Age, using in particular a model of boat that is represented by the [Hjortspring Boat](https://en.wikipedia.org/wiki/Hjortspring_boat).

## Design

Pytheas is designed following modules typically used in agent-based modelling frameworks such as [Mesa](https://github.com/projectmesa/mesa/blob/main/docs/overview.md). While Mesa comes with Agents, Space, a scheduler (Time) and Model as main modules, in Pyheas we use:

- Map: the space-like model, which changes in time. The agents in Pytheas move in continuous space and draw environmental data from three layers of data, one for wind, one for currents and one for waves. The three layers are grids of different granularity (depending on the underlying data) in space and time.
- Boat: the agent-like model, representing a boat moving from A to B. The interaction rules determining how the Boat moves in space are included either in a polar diagram, which is a table stating current speed and leeway based on wind speeds. The current speed is added linearly to movement. Waves do not affect movement, but they are recorded to asses _post hoc_ the feasibility of a travel.
- Travel: the scheduler, including aspects of the Mesa Time and Model modules. The Travel in Pytheas contains the movement of a Boat on the Map, but includes also rules for coastal navigation ("coast hugging") and night navigation.

As it should happen in true OOP, the different classes deal with what pertain to them. For example, the local wind speed at any given time and coordinate is a charactersitic of the Map, as such it will not be measured by the Boat. The Boat will receive it as an input within the Travel object. The bearing on the other hand is not an intrisinc property of the Map, but is something that pertains to the Boat. The function to calculate the bearing between two lat/lon will then be calculated within the Boat class.

## Simulation

Outside of the Pytheas package, a simulation file, `simulation.py` shows the base example to illustrate how to perform a travel. It comes with a `parameters.py` file containing the parameters and locations to run a simulation.
