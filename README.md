# WaniKaniScripts
This app reviews your progress in WaniKani https://www.wanikani.com outputs the details in little graphs
## Running
You can run using the following:
```docker run --rm --env APIKEY=[WaniKani_APIKEY] -v [/path/on/your/system]:/opt/WK_Review/Store -p 8050:8050 --name [Container Name] ghcr.io/amcclead7336/wanikaniscripts:main```
