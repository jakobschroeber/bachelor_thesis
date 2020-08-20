# Assessment MS

Assessment MS is a Docker-based assessment microservice for Moodle Learning Management Systems. The installation comes with an instance of [bitnami Moodle](https://hub.docker.com/r/bitnami/moodle/) and an instance of [Cassandra](https://hub.docker.com/_/cassandra), but allows for configuration of instances of these databases. It assumes though a Moodle LMS version 3.x is running mySQL 5.x and a Cassandra version 2.x.

## Installation

1. Open a new terminal window, and change the directory to where the installation will be

```bash
cd Drive:/my/installation/directory
```

2. Clone GitHub repository into that directory

```bash
git clone https://github.com/jakobschroeber/bachelor_thesis.git
```

3. Start building images and run docker-compose setup

```bash
docker-compose up -d
```

4. Wait for Moodle instance to become available at http://localhost:10080 (this may take up to 30 minutes)

5. Use the [default](https://hub.docker.com/r/bitnami/moodle/) MOODLE_USERNAME 'user' and default MOODLE_PASSWORD 'bitnami' to populate the Moodle instance with courses and users (for example, by creating a backup file of a course in the [Mount Orange](https://school.moodledemo.net/) school demo and restoring it inside your Moodle instance.

6. Create migration files (databases are initially empty)

```bash
docker exec assessment_ms sh -c "python manage.py makemigrations"
```

6. Apply migrations to the application database (SQLite)

```bash
docker exec assessment_ms sh -c "python manage.py migrate"
```

7. Apply migrations to the export database (Cassandra)

```bash
docker exec assessment_ms sh -c "python manage.py sync_cassandra"
```

8. Check whether courses and their users are availbale at http://localhost:8000/administration/courses/ (reload the page if you can see the page, but not your courses)

9. Populate the application database with some initial indicators, constructs and schedules

```bash
docker exec assessment_ms sh -c "python manage.py loaddata initial_data.json"
```

10. Open a new terminal window, change to the installation directory and start celery worker in order to carry out periodic assessments and exports

```bash
docker exec assessment_ms sh -c "celery -A app worker -l info"
```

11. Open a new terminal window, change to the installation directory and start celery-beat in order to provide celery with task messages

```bash
docker exec assessment_ms sh -c "celery -A app beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler"
```

12. Check at http://localhost:8000/assessment/indicators (Click on "Show results from database") whether assessment results are written to the application database (this is a setting of each indictor)

13. Connect to Cassandra at port 9042 to check whether assessment results are exported as expected (this is supposed to happen every ten minutes)

14. Check at http://localhost:8000/assessment/indicators (Click on "Show results from database") whether the already exported assessment results are deleted from the application database (this is supposed to happen once per hour)

15. The settings of when assessment results are exported and when already exported assessment results are deleted can be changed at http://localhost:8000/admin ("Periodic tasks"), in order to access it you need to create a Django admin account

```bash
docker exec -it <CONTAINER ID of assessment_ms container> python manage.py createsuperuser
```


## Cleaning up

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Stop docker-compose setup from running

```bash
docker-compose down
```

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Stop all running containers (if there is a problem)

```bash
docker ps -qa | xargs docker stop
```

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Clean up all built images, networks, caches, etc.

```bash
docker system prune -a
```

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Stop all running instances of celery worker

```bash
docker exec assessment_ms sh -c "celery -A app control shutdown"
```

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Stop celery-beat from sending task messages

```bash
docker exec assessment_ms sh -c "kill $(cat celerybeat.pid)"
```

