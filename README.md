# map.boerman.dev
This repo contains the source code for small Flask app that runs map.boerman.dev.

Its purpose is to show an Interactive Choropleth Map for the grafana dashboards at [data.boerman.dev](https://data.boerman.dev/)

The flask app generates a data object which is loaded into a leafletjs map. It is setup such that it is easy to add a new map.