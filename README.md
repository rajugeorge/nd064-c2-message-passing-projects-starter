# UdaConnect

## Overview

### Background

Conferences and conventions are hotspots for making connections. Professionals in attendance often share the same interests and can make valuable business and personal connections with one another. At the same time, these events draw a large crowd and it's often hard to make these connections in the midst of all of these events' excitement and energy. To help attendees make connections, we are building the infrastructure for a service that can inform attendees if they have attended the same booths and presentations at an event.

### Goal

You work for a company that is building a app that uses location data from mobile devices. Your company has built a [POC](https://en.wikipedia.org/wiki/Proof_of_concept) application to ingest location data named UdaTracker. This POC was built with the core functionality of ingesting location and identifying individuals who have shared a close geographic proximity.

Management loved the POC so now that there is buy-in, we want to enhance this application. You have been tasked to enhance the POC application into a [MVP](https://en.wikipedia.org/wiki/Minimum_viable_product) to handle the large volume of location data that will be ingested.

To do so, **_you will refactor this application into a microservice architecture using message passing techniques that you have learned in this course_**. It’s easy to get lost in the countless optimizations and changes that can be made: your priority should be to approach the task as an architect and refactor the application into microservices. File organization, code linting -- these are important but don’t affect the core functionality and can possibly be tagged as TODO’s for now!

### Technologies

- [Flask](https://flask.palletsprojects.com/en/1.1.x/) - API webserver
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
- [PostgreSQL](https://www.postgresql.org/) - Relational database
- [PostGIS](https://postgis.net/) - Spatial plug-in for PostgreSQL enabling geographic queries]
- [Kind](https://kind.sigs.k8s.io/) - kind is a tool for running local Kubernetes clusters using Docker container “nodes”.

## Running the app

The project has been set up such that you should be able to have the project up and running with Kubernetes.
We will also use Helm to install charts for Kafka

### Prerequisites

We will be installing the tools that we'll need to use for getting our environment set up properly.

1. [Install Docker](https://docs.docker.com/get-docker/)
2. [Set up a DockerHub account](https://hub.docker.com/)
3. [Set up kind](https://kind.sigs.k8s.io/docs/user/quick-start/)

### Environment Setup

To run the application, you will need a K8s cluster running locally and to interface with it via `kubectl`. We will be using Kind.

Follow the below steps to setup a Kind cluster. ( 'kind-config.yaml' is added to the root of the project ).

1. kind create cluster --config=kind-config.yaml --name=superkind

Afterwards, you can test that `kubectl` works by running a command like `kubectl describe services`. It should not return any errors.

### Setting up kafka using helm

we use Helm to setup kafka. Please follow the below instructions

1. `helm repo add bitnami https://charts.bitnami.com/bitnami`
2. `helm repo update`
3. ```
   helm install zookeeper bitnami/zookeeper \
     --set replicaCount=1 \
     --set auth.enabled=false \
     --set allowAnonymousLogin=true
   ```

```
Get the zookeeper DNS name and add to kafka config.

a. Get the zookeeper DNS name from below output. (Sample output).

ZooKeeper can be accessed via port 2181 on the following DNS name from within your cluster:

    zookeeper.default.svc.cluster.local

b. Add this value to the key 'KAFKA_HOST_CONSUMER' in deployment/kafka-configmap.yaml

```

4. ```
   helm install kafka bitnami/kafka \
     --set zookeeper.enabled=false \
     --set replicaCount=1 \
     --set externalZookeeper.servers=zookeeper.default.svc.cluster.local
   ```

```

Get the kafka DNS name and add to kafka config.

a. Get the internal kafka DNS name from below output. (Sample output).

Each Kafka broker can be accessed by producers via port 9092 on the following DNS name(s) from within your cluster:

    kafka-0.kafka-headless.default.svc.cluster.local:9092

b. Add this value to the key 'KAFKA_HOST_PRODUCER' in deployment/kafka-configmap.yaml

```

5. Get Kafka pod name using: `kubectl get pods --namespace default -l "app.kubernetes.io/name=kafka,app.kubernetes.io/instance=kafka,app.kubernetes.io/component=kafka" -o jsonpath="{.items[0].metadata.name}"`
6. Create topic (person-location): `kubectl --namespace default exec -it kafka-0 -- kafka-topics.sh --create --zookeeper zookeeper.default.svc.cluster.local:2181 --replication-factor 1 --partitions 1 --topic person-location` . Instead of 'kafka-0' use the pod name received from step 5. Instead of 'zookeeper.default.svc.cluster.local' use the url got from step 3

### Steps

1. `kubectl apply -f deployment/db-configmap.yaml` - Set up environment variables for the pods
2. `kubectl apply -f deployment/db-secret.yaml` - Set up secrets for the pods
3. `kubectl apply -f deployment/kafka-configmap.yaml` - Set up kafka environment variables for the pods
4. `kubectl apply -f deployment/postgres.yaml` - Set up a Postgres database running PostGIS
5. `kubectl apply -f deployment/udaconnect-api.yaml` - Set up the service and deployment for the API
6. `kubectl apply -f deployment/udaconnect-app.yaml` - Set up the service and deployment for the web app
7. `sh scripts/run_db_command.sh <POD_NAME>` - Seed your database against the `postgres` pod. (`kubectl get pods` will give you the `POD_NAME`)
8. `kubectl apply -f deployment/location-producer.yaml` - Set up the producer for location service.
9. `kubectl apply -f deployment/location-consumer.yaml` - Set up the consumer for location service.

Manually applying each of the individual `yaml` files is cumbersome but going through each step provides some context on the content of the starter project. In practice, we would have reduced the number of steps by running the command against a directory to apply of the contents: `kubectl apply -f deployment/`.

Note: The first time you run this project, you will need to seed the database with dummy data. Use the command `sh scripts/run_db_command.sh <POD_NAME>` against the `postgres` pod. (`kubectl get pods` will give you the `POD_NAME`). Subsequent runs of `kubectl apply` for making changes to deployments or services shouldn't require you to seed the database again!

### Verifying it Works

Once the project is up and running, you should be able to see 5 deployments and 6 services in Kubernetes:
`kubectl get pods` and `kubectl get services` - should both return `udaconnect-app`, `udaconnect-api`, `postgres`, `location-grpc` and `location-consumser`

These pages should also load on your web browser:

- `http://localhost:30001/` - OpenAPI Documentation
- `http://localhost:30001/api/` - Base path for API
- `http://localhost:30000/` - Frontend ReactJS Application

To test the location service, do the following.

1. Enable kafka console consumer.

```
kubectl --namespace default exec -it kafka-0 -- kafka-console-consumer.sh --bootstrap-server kafka.default.svc.cluster.local:9092 --topic person-location --consumer.config /opt/bitnami/kafka/config/consumer.properties

```

2. Get the pod name of location producer (pod starting with location-grpc-....)
3. Get into the command line of the location producer pod `kubectl exec -it <POD_NAME> -- /bin/sh`
   eg:- `kubectl exec -it location-grpc-84b497845-fzcwp -- /bin/sh`
4. Execute writer.py file : Run `python writer.py`
5. You should see the output at the kafka consumer console.
   sample output : `{"person_id": 1, "longitude": -122.29088592529297, "latitude": 37.55363082885742}`
6. You can also see the entry in the postgres database.

#### Deployment Note

You may notice the odd port numbers being served to `localhost`. [By default, Kubernetes services are only exposed to one another in an internal network](https://kubernetes.io/docs/concepts/services-networking/service/). This means that `udaconnect-app` and `udaconnect-api` can talk to one another. For us to connect to the cluster as an "outsider", we need to a way to expose these services to `localhost`.

Connections to the Kubernetes services have been set up through a [NodePort](https://kubernetes.io/docs/concepts/services-networking/service/#nodeport). (While we would use a technology like an [Ingress Controller](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/) to expose our Kubernetes services in deployment, a NodePort will suffice for development.)

## Development

### New Services

New services can be created inside of the `modules/` subfolder. You can choose to write something new with Flask, copy and rework the `modules/api` service into something new, or just create a very simple Python application.

As a reminder, each module should have:

1. `Dockerfile`
2. Its own corresponding DockerHub repository
3. `requirements.txt` for `pip` packages
4. `__init__.py`

### Docker Images

`udaconnect-app` and `udaconnect-api` use docker images from `isjustintime/udaconnect-app` and `isjustintime/udaconnect-api`. To make changes to the application, build your own Docker image and push it to your own DockerHub repository. Replace the existing container registry path with your own.

## Configs and Secrets

In `deployment/db-secret.yaml`, the secret variable is `d293aW1zb3NlY3VyZQ==`. The value is simply encoded and not encrypted -- this is **_not_** secure! Anyone can decode it to see what it is.

```bash
# Decodes the value into plaintext
echo "d293aW1zb3NlY3VyZQ==" | base64 -d

# Encodes the value to base64 encoding. K8s expects your secrets passed in with base64
echo "hotdogsfordinner" | base64
```

This is okay for development against an exclusively local environment and we want to keep the setup simple so that you can focus on the project tasks. However, in practice we should not commit our code with secret values into our repository. A CI/CD pipeline can help prevent that.

## PostgreSQL Database

The database uses a plug-in named PostGIS that supports geographic queries. It introduces `GEOMETRY` types and functions that we leverage to calculate distance between `ST_POINT`'s which represent latitude and longitude.

_You may find it helpful to be able to connect to the database_. In general, most of the database complexity is abstracted from you. The Docker container in the starter should be configured with PostGIS. Seed scripts are provided to set up the database table and some rows.

### Database Connection

While the Kubernetes service for `postgres` is running (you can use `kubectl get services` to check), you can expose the service to connect locally:

```bash
kubectl port-forward svc/postgres 5432:5432
```

This will enable you to connect to the database at `localhost`. You should then be able to connect to `postgresql://localhost:5432/geoconnections`. This is assuming you use the built-in values in the deployment config map.

### Software

To manually connect to the database, you will need software compatible with PostgreSQL.

- CLI users will find [psql](http://postgresguide.com/utilities/psql.html) to be the industry standard.
- GUI users will find [pgAdmin](https://www.pgadmin.org/) to be a popular open-source solution.

## Architecture Diagrams

Your architecture diagram should focus on the services and how they talk to one another. For our project, we want the diagram in a `.png` format. Some popular free software and tools to create architecture diagrams:

1. [Lucidchart](https://www.lucidchart.com/pages/)
2. [Google Docs](docs.google.com) Drawings (In a Google Doc, _Insert_ - _Drawing_ - _+ New_)
3. [Diagrams.net](https://app.diagrams.net/)

## Tips

- We can access a running Docker container using `kubectl exec -it <pod_id> sh`. From there, we can `curl` an endpoint to debug network issues.
- The starter project uses Python Flask. Flask doesn't work well with `asyncio` out-of-the-box. Consider using `multiprocessing` to create threads for asynchronous behavior in a standard Flask application.

```

```
