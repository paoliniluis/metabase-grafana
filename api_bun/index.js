import {serve} from 'bun';

serve({
  async fetch(request) {
    const body = await request.json();
    console.log(body)
    let fullMessage = ''
    let fullTail = ''

    if (request.url.includes('logs') && request.method === 'POST') {
      if (body.exception && body.mdc) {
        fullMessage = body.message + '\n' + body.exception.stacktrace
        fullTail = {
          trace_id: body.mdc.traceid,
          span_id: body.mdc.span_id,
          traceparent: request.headers.traceparent,
          exception: body.exception.exception_class
        }
      } else if (body.mdc) {
        fullMessage = body.message
        fullTail = {
          trace_id: body.mdc.traceid,
          span_id: body.mdc.span_id,
          traceparent: request.headers.traceparent,
        }
      } else {
        fullMessage = body.message
        fullTail = {
          traceparent: request.headers.traceparent,
        }
      }

      let reqMessage = {
        streams: [
          {
            stream: {
              source: body.source_host,
              level: body.level,
              logger: body.logger_name,
            },
            values: [
                [ body.timestamp.toString(), fullMessage, fullTail ],
            ]
          }
        ]
      }

      const response = await fetch(process.env['LOKI_HOST'], {
        method: "POST",
        body: JSON.stringify(reqMessage),
        headers: { "Content-Type": "application/json" },
      });

      return new Response({status: 200});
    }
  }
})