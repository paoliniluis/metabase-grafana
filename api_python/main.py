from fastapi import FastAPI, Request
from datetime import datetime

import os, databases

app = FastAPI()

database = databases.Database(f"postgres://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}/{os.environ['POSTGRES_DB']}")

@app.on_event("startup")
async def startup_event():
    await database.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await database.disconnect()


@app.post("/metabase")
async def getInformation(info : Request):
    req_info = await info.json()
    # print(req_info)
    if 'message' in req_info and ('GET' in req_info['message'] or 'POST' in req_info['message'] or 'PUT' in req_info['message'] or 'DELETE' in req_info['message']):
        # print(req_info["message"])
        splittedLine = req_info["message"].split(" ")
        # for i in range(0, len(splittedLine)):
        #     print(f'{i} - {splittedLine[i]}')
            
        values = dict()
        values['client'] = info['client'][0]
        timestamp = int(str(req_info["instant"]["epochSecond"]) + str(req_info["instant"]["nanoOfSecond"]))
        # humbly taken from https://stackoverflow.com/questions/15649942/how-to-convert-epoch-time-with-nanoseconds-to-human-readable
        values['request_timestamp'] = datetime.fromtimestamp(timestamp / 1e9)
        values['verb'] = splittedLine[0][splittedLine[0].find('m')+1:] # wipe colors
        values['endpoint'] = splittedLine[1]
        values['is_async'] = True if 'ASYNC' in req_info["message"] else False
        values['async_completed'] = splittedLine[4][:-1] if values['is_async'] else ""
        values['code'] = "" if splittedLine[2] == "" else int(splittedLine[2]) # we could extend this to grab any line, right now checking for nulls in code is useless

        positions = dict() # a dictionary to save the positions in the strings
        positions['time'] = 3
        positions['timeunit'] = 4
        positions['app_db_calls'] = 5
        positions['app_db_conns'] = 11
        positions['total_app_db_conns'] = 11
        positions['jetty_threads'] = 14
        positions['total_jetty_threads'] = 14
        positions['jetty_idle'] = 15
        positions['jetty_queued'] = 17
        positions['active_threads'] = 19
        positions['queries_in_flight'] = 26
        positions['queued'] = 27
        # positions['dw_db_connections'] = 35
        # positions['dw_db_total_conns'] = 35
        # positions['threads_blocked'] = 36

        if values['code'] == 200:
            values['time'] = float(splittedLine[positions['time']])
            values['timeunit'] = str(splittedLine[positions['timeunit']])
            values['app_db_calls'] = int(splittedLine[positions['app_db_calls']].replace("(", ""))
            values['app_db_conns'] = int(splittedLine[positions['app_db_conns']][0:splittedLine[positions['app_db_conns']].find("/")])
            values['total_app_db_conns'] = int(splittedLine[positions['total_app_db_conns']][splittedLine[positions['total_app_db_conns']].find("/")+1:])
            values['jetty_threads'] = int(splittedLine[positions['jetty_threads']][0:splittedLine[positions['jetty_threads']].find("/")])
            values['total_jetty_threads'] = int(splittedLine[positions['total_jetty_threads']][splittedLine[positions['total_jetty_threads']].find("/")+1:])
            values['jetty_idle'] = int(splittedLine[positions['jetty_idle']].replace("(", ""))
            values['jetty_queued'] = int(splittedLine[positions['jetty_queued']])
            values['active_threads'] = int(splittedLine[positions['active_threads']].replace("(", ""))
            values['queries_in_flight'] = int(splittedLine[positions['queries_in_flight']])
            values['queued'] = int(splittedLine[positions['queued']].replace("(", ""))
            query = '''INSERT INTO app_telemetry
            (
            client,
            request_timestamp,
            verb,
            endpoint,
            is_async,
            async_completed,
            status_code,
            response_time,
            time_unit,
            app_db_calls,
            app_db_conns,
            total_app_db_conns,
            jetty_threads,
            total_jetty_threads,
            jetty_idle,
            jetty_queued,
            active_threads,
            queries_in_flight,
            queued)
            VALUES
            (:client,
            :request_timestamp,
            :verb,
            :endpoint,
            :is_async,
            :async_completed,
            :code,
            :time,
            :timeunit,
            :app_db_calls,
            :app_db_conns,
            :total_app_db_conns,
            :jetty_threads,
            :total_jetty_threads,
            :jetty_idle,
            :jetty_queued,
            :active_threads,
            :queries_in_flight,
            :queued)
            '''
            # values['dw_db_connections'] = ""
            # values['dw_db_total_conns'] = ""
            # values['threads_blocked'] = ""
        elif values['code'] == 202: # this is the reason why I didn't include everything in the positions dict data structure
            for key in positions:
                positions[key] = positions[key] + 2
            values['time'] = float(splittedLine[positions['time']])
            values['timeunit'] = str(splittedLine[positions['timeunit']])
            values['app_db_calls'] = int(splittedLine[positions['app_db_calls']].replace("(", ""))
            values['app_db_conns'] = int(splittedLine[positions['app_db_conns']][0:splittedLine[positions['app_db_conns']].find("/")])
            values['total_app_db_conns'] = int(splittedLine[positions['total_app_db_conns']][splittedLine[positions['total_app_db_conns']].find("/")+1:])
            values['jetty_threads'] = int(splittedLine[positions['jetty_threads']][0:splittedLine[positions['jetty_threads']].find("/")])
            values['total_jetty_threads'] = int(splittedLine[positions['total_jetty_threads']][splittedLine[positions['total_jetty_threads']].find("/")+1:])
            values['jetty_idle'] = int(splittedLine[positions['jetty_idle']].replace("(", ""))
            values['jetty_queued'] = int(splittedLine[positions['jetty_queued']])
            values['active_threads'] = int(splittedLine[positions['active_threads']].replace("(", ""))
            values['queries_in_flight'] = int(splittedLine[positions['queries_in_flight']])
            values['queued'] = int(splittedLine[positions['queued']].replace("(", ""))
            if ('POST' in values['verb'] or 'PUT' in values['verb']) and 'query' not in values['endpoint']: # Doing a POST request to save something returns 202 but without DW connection
                # values['dw_db_connections'] = ""
                # values['dw_db_total_conns'] = ""
                # values['threads_blocked'] = ""
                query = '''INSERT INTO app_telemetry
                (
                client,
                request_timestamp,
                verb,
                endpoint,
                is_async,
                async_completed,
                status_code,
                response_time,
                time_unit,
                app_db_calls,
                app_db_conns,
                total_app_db_conns,
                jetty_threads,
                total_jetty_threads,
                jetty_idle,
                jetty_queued,
                active_threads,
                queries_in_flight,
                queued)
                VALUES
                (:client,
                :request_timestamp,
                :verb,
                :endpoint,
                :is_async,
                :async_completed,
                :code,
                :time,
                :timeunit,
                :app_db_calls,
                :app_db_conns,
                :total_app_db_conns,
                :jetty_threads,
                :total_jetty_threads,
                :jetty_idle,
                :jetty_queued,
                :active_threads,
                :queries_in_flight,
                :queued)
                '''
            else:
                values['dw_id'] = splittedLine[31] + "" + splittedLine[33]
                values['dw_db_connections'] = int(splittedLine[35][0:splittedLine[35].find("/")])
                values['dw_db_total_conns'] = int(splittedLine[35][splittedLine[35].find("/")+1:])
                values['threads_blocked'] = int(splittedLine[36].replace("(", ""))
                query = '''INSERT INTO app_telemetry
                (
                client,
                request_timestamp,
                verb,
                endpoint,
                is_async,
                async_completed,
                status_code,
                response_time,
                time_unit,
                app_db_calls,
                app_db_conns,
                total_app_db_conns,
                jetty_threads,
                total_jetty_threads,
                jetty_idle,
                jetty_queued,
                active_threads,
                queries_in_flight,
                queued,
                dw_id,
                dw_db_connections,
                dw_db_total_conns,
                threads_blocked)
                VALUES
                (:client,
                :request_timestamp,
                :verb,
                :endpoint,
                :is_async,
                :async_completed,
                :code,
                :time,
                :timeunit,
                :app_db_calls,
                :app_db_conns,
                :total_app_db_conns,
                :jetty_threads,
                :total_jetty_threads,
                :jetty_idle,
                :jetty_queued,
                :active_threads,
                :queries_in_flight,
                :queued,
                :dw_id,
                :dw_db_connections,
                :dw_db_total_conns,
                :threads_blocked)
                '''
        else: # Nullify everything else
            values['time'] = float(splittedLine[positions['time']])
            values['timeunit'] = str(splittedLine[positions['timeunit']])
            values['app_db_calls'] = int(splittedLine[positions['app_db_calls']].replace("(", ""))
            query = '''INSERT INTO app_telemetry
            (
            client,
            request_timestamp,
            verb,
            endpoint,
            is_async,
            async_completed,
            status_code,
            response_time,
            time_unit,
            app_db_calls)
            VALUES
            (:client,
            :request_timestamp,
            :verb,
            :endpoint,
            :is_async,
            :async_completed,
            :code,
            :time,
            :timeunit,
            :app_db_calls)
            '''
            # values['app_db_conns'] = ""
            # values['total_app_db_conns'] = ""
            # values['jetty_threads'] = ""
            # values['total_jetty_threads'] = ""
            # values['jetty_idle'] = ""
            # values['jetty_queued'] = ""
            # values['active_threads'] = ""
            # values['queries_in_flight'] = ""
            # values['queued'] = ""
            # values['dw_db_connections'] = ""
            # values['dw_db_total_conns'] = ""
            # values['threads_blocked'] = ""

        # print(values)
        await database.execute(query=query, values=values)