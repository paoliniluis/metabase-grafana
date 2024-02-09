Contents of this docker-compose
===============================


Metabase with several products of the grafana stack to monitor

Components:
1) Metabase
2) bun api: gets the log lines and sends that to Loki
3) python api: disabled for now, will get the log lines and populate prometheus with metrics
4) setup: will just set up Metabase
5) loki: log ingestor
6) prometheus: metrics scraper
7) tempo: traces ingestor
8) grafana: metrics visualizations

The Metabase server runs with a jmx, pyroscope and otel agents which send the data to tempo and prometheus. The bun api gets the log lines which are sent via log4j2 and sends that to loki

There's a pre-defined dashboard in grafana and also all the data sources get populated on start