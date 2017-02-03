# Sagebrew Web Backend #
Must run `sudo apt-get install postfix` for email to work correctly on local 
environment. 


# Reasoning Behind Character Counts #
We use 70 characters for titles and tags because the average sentence
is between 75 and 100 characters. For a title we don't want users 
writing sentences so we've dropped just below this threshold.

We use 120 characters for question titles and update titles 
to give users a bit of leeway when crafting a question. 
We are aiming to keep it under one sentence but don't want to 
hinder them too much.

We use 70 characters for tags because these shouldn't be sentences
either. However we use advocacy mission titles as tags right now
so we need to increase the allowable size. Potentially we will 
separate the 2 and have users tag related missions and tags 
separately. Allowing us to reduce the character count to 25 or 30.
