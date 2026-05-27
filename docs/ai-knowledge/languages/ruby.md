# Ruby Language Knowledge

Services: `src/email/`

## Version and Toolchain

- Ruby 3.4+
- Bundler for dependency management (`Gemfile` / `Gemfile.lock`)
- Framework: Sinatra

## Commands

| Task | Command | Working Directory |
|---|---|---|
| Install deps | `bundle install` | `src/email/` |
| Run | `bundle exec ruby email_server.rb` (or entry point in config) | `src/email/` |
| Test | `bundle exec rspec` or `bundle exec rake test` | `src/email/` |
| Lint | `bundle exec rubocop` | `src/email/` |
| Format | `bundle exec rubocop -a` | `src/email/` |

## OpenTelemetry Instrumentation

Uses the Ruby OTel SDK with Sinatra auto-instrumentation:

```ruby
require 'opentelemetry/sdk'
require 'opentelemetry/instrumentation/sinatra'
require 'opentelemetry/exporter/otlp'

OpenTelemetry::SDK.configure do |c|
  c.use 'OpenTelemetry::Instrumentation::Sinatra'
  c.add_span_processor(
    OpenTelemetry::SDK::Trace::Export::BatchSpanProcessor.new(
      OpenTelemetry::Exporter::OTLP::Exporter.new
    )
  )
end
```

OTLP HTTP exporter. Endpoint and protocol configured via:
- `OTEL_EXPORTER_OTLP_ENDPOINT`
- `OTEL_EXPORTER_OTLP_PROTOCOL` (default `http/protobuf`)

This configuration must be loaded before Sinatra routes are registered (before
`require 'sinatra'` or at the top of `application.rb`). If it is loaded after
routes, the Sinatra instrumentation will not wrap existing routes.

`Bundler.require` is used to load all gems from the `Gemfile` by group.

## Key Ruby Idioms

- `begin/rescue/ensure` for error handling with cleanup:
  ```ruby
  begin
    # work
  rescue StandardError => e
    span.record_exception(e)
    span.status = OpenTelemetry::Trace::Status.error(e.message)
    raise
  ensure
    span.finish
  end
  ```
- Read configuration exclusively from environment variables — no hardcoded
  endpoints or credentials.
- `Bundler.require` in `application.rb` to load gems by group.
- Freeze string literals at file top: `# frozen_string_literal: true`

## Common Failure Modes

| Symptom | Root Cause |
|---|---|
| `Bundler::GemNotFound` at container start | `Gemfile.lock` not committed or not copied into Docker image |
| No traces emitted | OTel exporter not registered in `application.rb` / config file |
| Sinatra routes not instrumented | OTel SDK configured after Sinatra routes registered |
| `LoadError` for OTel gems | Gem not in `Gemfile` or `bundle install` not run in Dockerfile |
| Missing spans for errors | `span.record_exception` not called in `rescue` block |

## Implementer Rules

1. Commit `Gemfile.lock` — the Docker image build depends on it for
   reproducibility.
2. Configure the OTel SDK before any Sinatra route definitions.
3. Never hardcode OTLP endpoint — read from `OTEL_EXPORTER_OTLP_ENDPOINT`.
4. Call `span.finish` (or use the block form) in all code paths — use
   `ensure` to guarantee it.

## Reviewer Checks

- `Gemfile.lock` absent or not in `.dockerignore` allowlist.
- OTel SDK configured after Sinatra `get`/`post`/`put` route definitions.
- Unrescued exceptions in route handlers (Sinatra returns 500 silently).
- Missing `span.finish` or `span.record_exception` in error paths.
- Gemspec version pins removed (causes non-deterministic builds).
- Hardcoded SMTP credentials or email addresses in source.
