# Behavior Shield Synthesis

## Package description
bin_linux (mac): uppaal binary modules 

car/shield: shield generation.

car/generate_cr_scenarios.py: putting the trajectory of the ego vehicle into a scenario.

car/generate_uppaal_models.py: converting a scenario into things in uppaal model.

## Prerequisites
Python 3.10

CommonRoad-io

ffmpeg 1.4 (conda install -c conda-forge ffmpeg)

imageio-2.37.0

Uppaal 5.1.10-beta5

# Troubleshooting
"MovieWriter ffmpeg unavailable". [Solution](https://stackoverflow.com/questions/60033397/moviewriter-ffmpeg-unavailable-trying-to-use-class-matplotlib-animation-pillo).
