# ADR-008: SaaS Multi-Tenancy & Secure Authentication Architecture

**Date:** 2026-07-09  
**Status:** Accepted  

## Context

VoxCore is designed to be a scalable, Voice AI backend for multiple independent developers (tenants). Initially, the system functioned as a single-user prototype with no authentication or session isolation. Any user who connected to the WebSocket received the exact same generic AI personality, and all connections were fully open to the public internet.

To evolve VoxCore into a **production-level SaaS service**, we required a system that achieved the following:
1. **Tenant Isolation:** Client A's users must never be able to access, modify, or pollute Client B's session data.
2. **Dynamic Personas:** The AI's behavior, instructions, and capabilities must be dynamically injected per tenant connection based on their database configuration.
3. **Secure Handshakes:** The WebSocket connection must be secure and protected from Denial of Service (DoS) and Ticket Replay attacks without forcing the end-user (browser) to expose sensitive API keys.
4. **Zero-Cost Scaling:** Operations and persistence must be highly optimized to run on $0 free-tier cloud architectures (e.g., Oracle OCI), relying strictly on SQLite/SQLAlchemy without invoking heavy external infrastructure like Redis for state management.

## Decision

We implemented a **Strict Domain-Driven Design (DDD)** authentication flow relying on an **Ephemeral Ticketing System** and **Composite Database Keys**.

### 1. The Ephemeral Ticket Handshake (Server-to-Server)
Passing a Master API Key from a public browser to our WebSocket server is a catastrophic security vulnerability, as browsers cannot conceal outgoing request payloads. 

To solve this, we implemented a 2-step ticketing system:
- **Step 1:** The Tenant's *backend server* makes an authenticated `POST /v1/auth/ticket` request to VoxCore using their secret Master API Key in the `Authorization` header.
- **Step 2:** VoxCore authenticates the Tenant, creates a short-lived (30-second) `ticket_uuid` in a dedicated `ephemeral_tickets` database table, and returns this UUID.
- **Step 3:** The Tenant passes this `ticket_uuid` to their frontend browser application. The browser opens a WebSocket connection to VoxCore `ws://.../v1/voice?ticket={ticket_uuid}`. VoxCore consumes the ticket, destroys it in the database, and begins the Voice AI session.

### 2. Multi-Worker ASGI Safety via Database Atomicity
A critical flaw of using in-memory Python dictionaries for storing tickets is state desynchronization. In production, ASGI servers (Uvicorn/Gunicorn) spawn multiple isolated worker processes. A ticket saved in Worker 1's memory is invisible if the WebSocket reconnect hits Worker 2.

By storing short-lived tickets in the SQLite `ephemeral_tickets` table and utilizing explicit SQLAlchemy two-step transactions with `.with_for_update()`, we guarantee 100% atomic consumption across any number of workers without race conditions.

### 3. SQLite Concurrency & Storage Hardening
Because Voice AI generates massive bursts of micro-writes (appending user transcripts, logging metrics), standard SQLite defaults would cause `database is locked` operational timeouts. We implemented three strict database optimizations:
- **WAL Mode:** We explicitly hooked SQLAlchemy to execute `PRAGMA journal_mode=WAL;` and `PRAGMA synchronous=NORMAL;` on connection, allowing concurrent readers and writers.
- **Busy Timeout:** We increased the connection `timeout` argument to 30 seconds, allowing queries to queue gracefully during load spikes.
- **Anti-Bloat Background Pruning:** If a browser drops the connection before consuming a ticket, the ticket remains in the DB forever. We implemented an `asyncio` background task that automatically sweeps and deletes expired tickets every 15 minutes to prevent SQLite storage exhaustion.

### 4. Tenant Persona Injection
When a valid ticket is consumed, VoxCore retrieves the `project_id` and the associated dynamic `domain_persona` for that specific tenant. The `SessionMemoryManager` was modified to map unique `ContextBuilder` instances to individual `session_id`s, ensuring that the AI persona strictly conforms to the tenant's configuration for the duration of that WebSocket lifecycle.

## Consequences

- **Positive:** VoxCore is now a true, secure SaaS multi-tenant backend. A single deployed instance can securely serve dozens of different applications with unique personas.
- **Positive:** Operations are completely robust for ASGI multi-worker scaling while strictly adhering to a $0 footprint (No Redis required).
- **Positive:** Complete isolation of session memory using strict `WHERE project_id = ? AND session_id = ?` query logic (to be fully realized in the incoming `IStore` database refactor).
- **Negative:** Slightly increased latency during the initial connection due to the two-step backend ticket handshake.
- **Negative:** Increased SDK complexity for clients, as they must now build a backend proxy route to fetch the ticket rather than connecting from the frontend directly. This trade-off is standard for production APIs (e.g., Stripe, Twilio) and is an acceptable necessity for security.
