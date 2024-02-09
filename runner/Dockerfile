FROM eclipse-temurin:11-jre as runner

ENV FC_LANG en-US LC_CTYPE en_US.UTF-8
ARG version

WORKDIR /app/

# ADD https://raw.githubusercontent.com/paoliniluis/metabase-trino/main/metabase-starburst/run_metabase.sh .
ADD ./run_metabase.sh .
# ADD https://github.com/firebolt-db/metabase-firebolt-driver/releases/download/1.0.12/firebolt.metabase-driver-1.0.12.jar plugins//firebolt.metabase-driver-1.0.12.jar
# ADD https://github.com/starburstdata/metabase-driver/releases/download/2.0.1/starburst-2.0.1.metabase-driver.jar plugins/starburst-2.0.1.metabase-driver.jar
# ADD https://github.com/exasol/metabase-driver/releases/download/1.0.4/exasol.metabase-driver.jar plugins/exasol.metabase-driver.jar
# ADD https://repo1.maven.org/maven2/com/exasol/exasol-jdbc/7.1.16/exasol-jdbc-7.1.16.jar plugins/exasol-jdbc-7.1.16.jar
# ADD https://github.com/ClickHouse/metabase-clickhouse-driver/releases/download/1.1.3/clickhouse.metabase-driver.jar plugins/clickhouse.metabase-driver.jar
# ADD https://github.com/Xeograph/metabase-ocient-driver/releases/download/v1.0.0/ocient.metabase-driver.jar plugins/ocient.metabase-driver.jar

RUN apt-get update && \
  apt-get upgrade -y && \
  apt-get install -y ca-certificates ca-certificates-java fonts-noto && \
  apt-get clean && \
  curl https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem -o /usr/local/share/ca-certificates/rds-combined-ca-bundle.pem && \
  curl https://cacerts.digicert.com/DigiCertGlobalRootG2.crt.pem -o /usr/local/share/ca-certificates/DigiCertGlobalRootG2.crt.pem && \
  update-ca-certificates && \
  mkdir -p /plugins && chmod a+rwx /plugins && \
  keytool -list -cacerts && \
  curl https://downloads.metabase.com/enterprise/${version}/metabase.jar -o metabase.jar && \
  chmod +x run_metabase.sh && \
  chmod -R a+rwX /app/

# RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends  && \
#     # cleaning everything to reduce container size
#     apt-get autoremove -y && apt-get autoclean && \
#     rm -rf /var/lib/apt/lists/* && \
#     # providing permissions to the nobody user
#     curl https://downloads.metabase.com/enterprise/v{version}/metabase.jar -o metabase.jar && \
#     chmod +x run_metabase.sh && \
#     chmod -R a+rwX /app/

# expose our default runtime port
EXPOSE 3000

# run it
ENTRYPOINT ["/app/run_metabase.sh"]