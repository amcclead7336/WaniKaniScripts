# WaniKaniScripts
This app reviews your progress in WaniKani https://www.wanikani.com outputs the details in little graphs
## Runing
You can run using the following:
```docker run --rm --env APIKEY=[WaniKani_APIKEY] -v [/path/on/your/system]:/opt/WK_Review/Store -p 8050:8050 --name [Container Name] wk_review:v0.0.1```
