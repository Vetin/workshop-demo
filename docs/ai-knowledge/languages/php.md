# PHP Language Knowledge

Services: `src/quote/`

## Version and Toolchain

- PHP 8.4
- Composer for dependency management (`composer.json` / `composer.lock`)
- Framework: Slim Framework

## Commands

| Task | Command | Working Directory |
|---|---|---|
| Install deps | `composer install` | `src/quote/` |
| Run | `php -S 0.0.0.0:8080 -t public/` (dev) | `src/quote/` |
| Test | `composer run test` or `./vendor/bin/phpunit` | `src/quote/` |
| Lint (CS) | `./vendor/bin/phpcs` | `src/quote/` |
| Static analysis | `./vendor/bin/phpstan analyse` | `src/quote/` |
| Format | `./vendor/bin/phpcbf` | `src/quote/` |

## OpenTelemetry Instrumentation

Uses PHP auto-instrumentation via the OTel PHP extension:

```
OTEL_PHP_AUTOLOAD_ENABLED=true
```

This env var **must** be set for any instrumentation to activate. Without it,
all OTel code is a no-op.

Manual tracer API for custom spans:

```php
$tracer = \OpenTelemetry\API\Globals::tracerProvider()->getTracer('quote');
$span = $tracer->spanBuilder('calculateQuote')->startSpan();
$scope = $span->activate();
try {
    // work
} catch (\Throwable $e) {
    $span->recordException($e);
    $span->setStatus(\OpenTelemetry\API\Trace\StatusCode::STATUS_ERROR, $e->getMessage());
    throw $e;
} finally {
    $span->end();
    $scope->detach();
}
```

OTLP HTTP exporter configured via env vars:
- `OTEL_EXPORTER_OTLP_ENDPOINT`
- `OTEL_EXPORTER_OTLP_PROTOCOL` (default `http/protobuf`)

The manual tracer must only be used **after** the SDK has been initialized via
the autoload mechanism. Do not call `\OpenTelemetry\API\Globals::tracerProvider()`
before the autoloader has run.

## Key PHP Idioms

- `declare(strict_types=1)` at the top of every PHP file.
- PSR-4 autoloading — class names match directory structure under `src/`.
- Typed properties and return types on all class methods:
  ```php
  private string $currency;
  public function getQuote(int $items): float { ... }
  ```
- Slim route handlers return `ResponseInterface`:
  ```php
  $app->get('/quote', function (Request $req, Response $res): Response {
      // ...
      return $res->withStatus(200)->withJson($data);
  });
  ```
- Use `\Throwable` (not `\Exception`) in catch blocks to catch both errors
  and exceptions.

## Common Failure Modes

| Symptom | Root Cause |
|---|---|
| No traces, no instrumentation active | `OTEL_PHP_AUTOLOAD_ENABLED` env var not set in container |
| `Composer\Package\PackageNotFoundException` | `composer.lock` not committed or `composer install` not run in Dockerfile |
| Manual tracer returns no-op | OTel autoload not complete before manual API call; check init order |
| Type error at runtime | `declare(strict_types=1)` absent; implicit type coercion in strict operation |
| `span->end()` not called | Missing `finally` block; span leaks and is never exported |

## Implementer Rules

1. Always set `OTEL_PHP_AUTOLOAD_ENABLED=true` in the Dockerfile `ENV` or
   docker-compose environment.
2. Commit `composer.lock` — the Docker build depends on it.
3. Every custom span must be ended in a `finally` block and scope detached.
4. Never access `$_POST`, `$_GET`, `$_SERVER['HTTP_*']` for span attribute
   values without sanitizing PII first.
5. Keep `declare(strict_types=1)` in all PHP files.

## Reviewer Checks

- `OTEL_PHP_AUTOLOAD_ENABLED` missing from Dockerfile or env config.
- `composer.lock` not committed.
- `$span->end()` or `$scope->detach()` outside a `finally` block.
- `$_POST`/`$_GET`/`$_REQUEST` values used directly as span attributes (PII risk).
- Type coercion bugs: integer math done on strings without explicit cast.
- Slim route handler does not return `ResponseInterface`.
- `\Exception` caught instead of `\Throwable` (misses `\Error` subclasses).
