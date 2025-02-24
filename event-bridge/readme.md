# Event Bridge
This project acts as the event bridge between the minio object storage and the executor. It uses poll mechanism to identify the newly created objects of type *.json in the minio bucket with name fhir

It looks in the following path fhir/TODO
and sends the HTTP Request to the executor service endpoint with object key
