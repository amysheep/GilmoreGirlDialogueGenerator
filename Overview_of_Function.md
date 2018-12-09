# GilmoreGirlsDialogueGenerator
This APP generates text predictions from LSTM neural network model trained on Gilmore Girls TV series scripts (all seasons) by the two main characters -- Rory and Lorelai Gilmore. 

The model is trained using Keras in Python and tensorflow GPU backend. By running the 'ui/server.py' file, a Web UI will be created to interactively take user input sequence as seed and output the desired length of generated text. 

The tool allows us to compare prediction outcomes under different 'temperature/diversity' parameters. In addition, we can compare the different results from the same seeding sequence by the two main characters. 
