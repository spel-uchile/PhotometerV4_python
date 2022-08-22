# PhotometerV4_python
Python implementation of the AOD retrieval algorithms (include ozone affected bands model)

## About
This is a python implementation of the code developed in [1]. The scrips are in "Code" folder. Here, we provide a small description of those codes:

- aeronet_processing_data.py: Takes de data provided by AERONET, extract the main features, and creates a .json file.
- aod_display: Using the .json files and estimates the AOD as [1] and plot the daily AOD profiles.
- aod_display_v4.py: Using the .json files and estimates the AOD and plot the daily AOD profiles under V4 type data. 
- calibration_class.py: Code used to calculate the calibration constants as [1].
- calibration_v4.py: Code used to calculate the calibration constants for the V4 data type.
- measurement_class.py: create an object to process data obtained from V4 Photometer.
- ozone_model.py: functions to process ozone model.
- processing_data.py: scrip to fix data depending on the available information measurements.

The end scrips are aod_display.py or aod_display_v4.py.
## References

[1] Garrido, C.; Toledo, F.; Diaz, M.; Rondanelli, R. Automated Low-Cost LED-Based Sun Photometer for City Scale Distributed Measurements. Remote Sens. 2021, 13, 4585. https://doi.org/10.3390/rs13224585 
