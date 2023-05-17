This script collects data from a specific template on a wiki and generates a CSV with total values. The template used is [Mall:Core metrics](https://se.wikimedia.org/wiki/Mall:Core metrics). The resulting CSV contains number of events (= number of templates) for a project and the sum of statistics for all events, such as number of editors and content added.

## How to run

[Pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikibot) is required to run. Install with `pip install -r requirements.txt`. Using [venv](https://docs.python.org/3/library/venv.html) is recommended.

Run the script with
```
./wiki_to_csv.py -y 2022
```
where `2022` is the year for which you want to collect metrics. All other parameters are hard coded for [Wikimedia Sveriges wiki](https://se.wikimedia.org/).

The output will look something like this:
```
,Wikipedia för hela Sverige 2022,Wikipedia i utbildning 2022
meta_data,2023-02-13 (6 st. event),2023-02-13 (1 st. event)
deltagare_♀,34,0
deltagare_♂,25,0
deltagare_⚥,0,0
deltagare_?,28,3
deltagare_total,87,3
redigerare_♀,0,0
redigerare_♂,0,0
redigerare_⚥,0,0
redigerare_?,0,3
redigerare_total,0,3
org_♀,7,0
org_♂,4,0
org_⚥,0,1
org_?,0,0
org_total,11,1
content_wp,0,0
content_com,0,0
content_wd,0,11
content_other,0,0
content_total,0,11
```

You can specify an "order file" as a parameter which will be used to sort the projects in the output. This makes it easier to copy to the target table. Empty lines in the order file inserts dummy projects called "_0", "_1", etc.

## Why "global-metrics"?

When this script was created the metrics were called "Global metrics". They've since been replaced by "Core metrics".
