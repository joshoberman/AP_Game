AP_Game
=======
Pygame game used for a psychology experiment testing implicit musical note category learning in a video game context. Subject plays through 12 levels, trying to anticipate alien entry points based on the notes being played.

To run from command line/terminal, just set your current directory to this repo and run

  <code> python game_v4.py </code>
  
  You will be prompted to enter a subject number, and the condition will be generated randomly.
  
The data from this experiment is automatically transferred to the Subject Files.  Each file has the Subject's condition, their score across levels, and folders containing their trajectories in pixels for each trial (more specifically, their location in pixels from the first time they hear each alien to when the alien dies).

The scores across levels by condition can be analyzed in R by sourcing the readConditions.R file and running/assigning a variable to readAll() with the argument being the maximum subject number in the repository (i.e. if Subject 40, readAll(40)). There is a commented place in the code where specific subjects can be excluded from this analysis.

The median absolute deviations, or MADs, in pixels from the range in which the enemy can be successfully shot by the player can be analyzed across subjects by sourcing the readTrajectories.R file and running readEverything, and storing this in a variable called, for instance, trajects.  This code is robust and will run without arguments, produce histograms of the distribution of MADs across conditions, and will produce a plot called "deviationsPlot) with regresssion lines.  The function returns a list of 3 objects, first a data frame with subject,condition, and MAD by level, second the linear model for the regression on the series 1:12 for the mean MADs of condition 1, and third the linear model for the regresiion on the series 1:12 for the mean MADs of condition 2
