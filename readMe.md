to use this application
1. clone the code to your local machine
2. create a virtual env. and install the requirements.txt 
using pip install -r requirements.txt
3. create a .env file in the same directory as settings.py and grab env variables from it, you can follow this link
https://alicecampkin.medium.com/how-to-set-up-environment-variables-in-django-f3c4db78c55f
-----------------------------------------
This Project will be build upon the next 3 chapters of Django 3 by example book ch 4,5,6
----------------------------------------------------------------------------------------
More details soon ..
**ch4**
1. add user authentication system, change and reset password, register new user, extend user to create profiles using django signals to create a new profile on creatign a new user automatically
2. configure local server to run on https protocol
3. add social authentiication to the website using facebook, google, twitter, ....


**ch5**
1. create Image model with many to many realtion to both user  model.
2. create a javascript booklet to allow users to share and save images from other sites.
3. create cutom ajax decorator and paginator.
4. create an infinte scroll functionality.
5. create a web crawler to download and save images from other sites, Note i will make it a celery task soon to run in the background.
6. create custom forms with custom validations
7. send ajax requests to like/dislike images to avoid loading page every time


**ch6**
1. create the following/follwers subsystem
2. create activity stream using generic relationship to store users actions and feed them
3. use signals for database denormalization
4. use Redis to store item views,and to buils an image ranking with Redis
and many many more ..
*run HTTPS locally*
python manage.py runserver_plus --cert-file cert.crt 