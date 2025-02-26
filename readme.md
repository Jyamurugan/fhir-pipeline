# FHIR Pipeline Orchestration (Local)

## Technologies used
    synthea (For data generation)
    minio (for s3 like storage)
    python (for transformation & data loads)
    python schedulre (for checking new files)

## binaries
These binaries are required for the the development. These are windows versions
1. [minio]()

## Test data setup (Synthea)
Dowload it from here [Synthea](https://github.com/synthetichealth/synthea/wiki/Basic-Setup-and-Running) JAR version.
Need to install latest version of java

### minio
Instructions available at [here]("https://min.io/docs/minio/windows/index.html")
Download link [link](https://dl.min.io/server/minio/release/windows-amd64/minio.exe) to this directory
Open cmd and run
```
minio.exe server /path/to/storage
// Example
minio.exe server D:\code\fhir-pipeline\object-storage
```

```
API: http://192.168.1.5:9000  http://127.0.0.1:9000
   RootUser: minioadmin
   RootPass: minioadmin

WebUI: http://192.168.1.5:62177 http://127.0.0.1:62177
   RootUser: minioadmin
   RootPass: minioadmin
```
### FHIR data set
Downloaded from sample of [synthea]("https://synthea.mitre.org/downloads")

### Bucket structure
Two buckets
1. FHIR
2. Archive

FHIR will have 2 sub paths
1. TODO
2. ERROR

Archive will have many sub paths (Partition by Date) Format YYYY-MM-DD. For Example
1. 2025-02-24 Processed at 24 Feb 2025
2. 2025-02-25 Processed at 25 Feb 2025

Archive by the using the compression technique (gz)


### Running
```
minio.exe server D:\code\fhir-pipeline\object-storage
cd event-bridge
poetry run python src\main.py
cd fhir-to-claims-processor
poetry run python src\main.py
```
