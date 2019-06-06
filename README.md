# Alexa Skills
Repo to hold code for alexa skills

## Family Jobs Skill
This skill will allow a user to ask Alexa for a random chore for the kids. 

The dynamoDB schema is simple and contains a Job ID, a Job Name, a Job Description and a column for each child that stores a boolean to determine if that job is suitable for that child. If the job is not suitable, a new job is retrieved. 