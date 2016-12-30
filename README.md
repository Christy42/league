The league structure should be as follows:
We have leagues folder
    This contains a file that simply holds the season number
    Then we have the seasons folder containing all the leagues for that season.  We start at 1 etc.
        Then we have a directory for each tier of the game.  We will start with 3
            This directory will contain the files relating to cup matches
            The folders in here will be one for each league
                Finally this will contain a csv containing the league ordering called table
                A file containing the teams user ids called team
                The schedule for the league called schedule


Later on files will be created containing the play off matches and the demotions/promotions
These will be kept within each individual league folder.
The play off file will contain the ordering of matches
The promotions file will contain anyone getting promoted into this division (at the end of the given season)
The demotions file will contain anyone getting demoted into this division (at the end of the given season)
A function will use the play off file to update the promotions/demotions files as they are played.