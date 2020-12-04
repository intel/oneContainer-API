## queue service for onecontainer-api

The queuing service is setup as 4 microservices that include:

- redis - oca_redis
- redis queue - oca_queue
- redis queue API - oca_queue_api
- redis queue dashboard - dashboard

The services are orchestrated using `docker-compose` and uses `node-net` bridge
network to talk to each other.

To instantiate the service, run:

```bash
make
```
To see the queue status, a dashboard is available at : localhost:5555

Once the service is up and running, to test use:

```bash
curl localhost:5057:/queue
```

## testing queue with a backend service

1. Start queuing service:

```bash
cd ./async_queue
```

```bash
make
```
If everything well, sysout will be something like:

```bash
Recreating oca_queue_api ... done
Starting oca_redis       ... done
Recreating dashboard      ... done
```

2. Start the backend service - here its a stub service that has 3 urls:

```bash
cd tests/service_stub

```bash
make
```

localhost:5055/fast
localhost:5055/slow
localhost:5055/very_slow

eg: api of the backend service

```bash
curl -d '{"key1":"val1"}' -X POST http://localhost:5055/fast
```

Response:

```json
{
  "args": {},
  "json": {
    "key1": "val1"
  },
  "msg": "success: POST with args service success!",
  "pi": 3.1415826535897198,
  "time_taken": 0.06674957275390625,
  "type": "fast"
}


3. POST a new job to the queue

```bash
curl -X POST -H "Content-Type: application/json" -d @./sample2.json localhost:5057/queue
```
Response:

```json
{"id":"c2be3ffd-9647-4f34-8292-9e9f10255008","status":"queued","position":2}%
````


4. check for info on the jobs

```bash
curl -X OPTIONS localhost:5057/queue
```
Response:

```json
{"name":"queue_info","size":2,"job_ids":["3af40ed0-ab31-4f02-93ed-a4df034cdede","c2be3ffd-9647-4f34-8292-9e9f10255008"]}
```

5. get the job results


```bash
curl -X GET localhost:5057/queue/625dcd9d-62b6-4854-9fdd-279567bbff48
```
Response:

```json
{"status":"queued","result":null}
```

### Test data

The directory `./async_queue/tests/data` has a set of json test data that can be used to query different backends.


### External backends

external.json and external2.json has examples of an external service

```bash
cat external.json
```
```json
{
   "url":"http://numberoca.com/random/year",
   "req_type":"get",
   "ttl":"700"
}
```
To test the queue with this data try sending a bunch of requests to the service using::

```bash
for i in `seq 1 20`
	do
		curl -X POST -H "Content-Type: application/json" -d @./external.json localhost:5057/queue
	done 
```

If you are montoring the dashboard you will see the queue being populated, once the jobs are done, the UUID of a job can be used to poll for the result.

