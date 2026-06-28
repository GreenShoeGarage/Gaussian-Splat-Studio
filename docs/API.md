# API Reference

Base URL:

```text
http://localhost:8000
```

## Health

```http
GET /api/health
```

## Projects

```http
GET /api/projects
POST /api/projects
GET /api/projects/{pid}
PATCH /api/projects/{pid}
DELETE /api/projects/{pid}
```

## Upload

```http
POST /api/projects/{pid}/upload
```

## Generate

```http
POST /api/projects/{pid}/generate
GET /api/jobs/{jid}
POST /api/jobs/{jid}/cancel
```

## Engines

```http
GET /api/engines
GET /api/engines/{engine_id}/preflight
PATCH /api/projects/{pid}/engine
```

## Validation

```http
POST /api/projects/{pid}/verify-output
```

## Downloads

```http
GET /api/projects/{pid}/download/{artifact}
GET /api/projects/{pid}/export-bundle
```
