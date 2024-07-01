# flask-microblog
Micro social media created using Flask

Features: 
1. User authentication and autherization implemented using Flask-login.
    Includes user details validations, password hashing and password reset using one time token. 
2. Follow, unfollow (Many to Many relationship) and view other users registered on the application. 
3. Send text messages other users, view sent and received messages. 
4. Complete CRUD of posts containing text/text+image using SQLAlchemy ORM and pillow library. 
5. Pages to see followed users posts or all public posts.
6. View, like/unlike, comment, and view likes/comments of any posts asynchronosly. 
7. Full text search feature implemented using Elasticsearch. 
8. Translate user posts in non english language.    
9. Export user posts to registered @gmail address in json format. Implemented using redis, and RQ. 


Tech Used: 

Python Flask framework, MySQL DB, SQLAlchemy(Flask-sqlalchemy) ORM, Flask-login, flask-migrate, Elasticsearch, 
redis, RQ for task queuing, Bootstrap-5, JS for asynchronous operations, 
MS translator API service, google SMPT for mailing services, 
and Docker for containarization and container deployment on google cloud run. 

