# Post-Production Localization Platform — High-Level Design

## 1. Purpose

A platform to **order and fulfill** post-production localization assets for media titles across vendors and regions.

Supported work types include:

- Closed captioning (CC)
- Subtitling
- Audio description (AD)
- Metadata translation (localized descriptions for different device sizes)

**Creating a workorder places an order.** Producing the asset (translation, captioning, review, delivery) is a separate, long-running fulfillment process.

---

## 2. Domain model

| Concept | Meaning |
|---|---|
| **Source (proxy)** | Low-resolution media used for processing (cost and security). Proxy readiness is often a gate before work can proceed. |
| **Workorder config** | Reusable settings: vendor, region, work type, source/target language, and related fulfillment rules. Defines *how* work is done. **Required before any workorder can be created.** |
| **Workorder** | A concrete order for a title/episode, bound to a config. Carries lifecycle status through fulfillment to `COMPLETED` or `CANCELLED`. |
| **Airing event** | Signal from upstream scheduling that a title will air in a market/language. One of two ways to **create** a workorder (the other is the UI)—not a fulfillment step by itself. |

**Order vs asset:** a successful workorder create means the order exists—not that metadata (or CC/AD) has been produced.

---

## 3. Core sub-flow

Every piece of work follows the same spine:

```
Create config  →  Create workorder  →  Fulfil workorder
     │                    │                    │
  prerequisite      order is placed      asset is produced
```

1. **Config must exist first.** Without a matching config (vendor, region, work type, languages, etc.), nothing further can proceed.
2. **Workorder create** always lands on the **domain service**, which owns persistence and starting fulfilment—regardless of trigger.
3. **Fulfilment** is the long-running saga (orchestration + Temporal + domain services).

---

## 4. Where the airing event fits

A workorder can be created in **two equivalent ways**. Both converge on the **same domain-service create API** and start the same fulfilment.

| Path | When | Flow |
|---|---|---|
| **Angular UI (manual)** | Airing is **not yet scheduled**, but the team will air the show and wants post-production done **in advance**. | Frontend → **BFF** → **Domain service** |
| **Airing event (automatic)** | No workorder was created manually, and later an **airing is scheduled**. | Airing → **Domain service** (directly) |

On create, the domain service uses **external data service** to **enrich** the request (title/catalog/schedule and related facts), then talks to **DB service** to persist the workorder and related state.

```
                    ┌──────────────────────────┐
                    │   Workorder config       │
                    │   (must already exist)   │
                    └────────────┬─────────────┘
                                 │
              ┌──────────────────┴──────────────────┐
              │                                     │
              ▼                                     ▼
   ┌─────────────────────┐             ┌─────────────────────────┐
   │ Angular UI (manual) │             │ Airing event (auto)     │
   │ → BFF               │             │ (no BFF)                │
   └──────────┬──────────┘             └────────────┬────────────┘
              │                                     │
              └──────────────────┬──────────────────┘
                                 ▼
                    ┌──────────────────────────┐
                    │ Domain service           │
                    │  • enrich via external   │
                    │    data service          │
                    │  • persist via DB service│
                    │  • start fulfilment      │
                    └──────────────────────────┘
```

**Role of the airing event:** an **order-creation trigger** when the team did not pre-create the workorder. It is not required when work was already ordered in advance via the UI. After create, fulfilment does not care which path was used.

---

## 5. System context

```
┌─────────────────────┐              ┌──────────────────────┐
│  Angular Frontend   │              │ External / airing    │
└──────────┬──────────┘              └──────────┬───────────┘
           ▼                                    │ airing event
┌─────────────────────┐                         │
│  BFF (Java)         │                         │
│  UX APIs only       │                         │
└──────────┬──────────┘                         │
           │                                    │
           │ create / update / read             │
           └─────────────────┬──────────────────┘
                             ▼
                  ┌─────────────────────────┐
                  │ Domain services (Java)  │
                  │ Metadata / CC / AD / …  │
                  └───┬──────────┬──────┬───┘
                      │          │      │
         enrich/read  │          │      │ start / advance fulfilment
                      │          │      │ (only these talk to Temporal)
                      ▼          ▼      ▼
        ┌────────────────┐  ┌────┴────┐  ┌──────────────────────────┐
        │ External Data  │  │   DB    │  │ Orchestration service    │
        │ Service        │  │ Service │  │ + Temporal               │
        │ schedules,     │  │ configs,│  │ DSL, workflows, waits,   │
        │ catalog, …     │  │ WOs,    │  │ task queues              │
        └────────────────┘  │ status  │  └────────────┬─────────────┘
                            └─────────┘               │
                                                      │ activities
                                                      ▼
                                           Domain services (same)
                                           run steps → DB / AI

        ┌──────────────────────────┐
        │ AI Metadata (Python)     │  ← called by metadata domain service only
        └──────────────────────────┘

Vendor review app (separate): human-in-the-loop wait during fulfilment.
```

**Access rules:**

- BFF never talks to DB, external data, or Temporal—only to **domain services**.
- **Only domain services and the orchestration service interact with Temporal.**
- DB and external data are reached only from domain services (persist / enrich).
- Airing and UI both land on domain services for create; domain then starts fulfilment via orchestration/Temporal.

---

## 6. Logical components

| Component | Responsibility |
|---|---|
| **Frontend** | Create/read/update configs and workorders (single or Excel bulk); show status. Used for advance ordering when airing is not yet scheduled. |
| **BFF** | Frontend-facing API only. Forwards to the appropriate **domain service**. Does **not** call DB, external data, or Temporal. |
| **Domain services** (metadata, CC, AD, …) | **Single entry for order create/update** (from BFF or airing) and **fulfilment workers**. Enrich via external data; persist via DB; start/advance fulfilment with **orchestration/Temporal**; call AI when needed. |
| **DB service** | System of record for configs, workorders, sources, status history, and work products. Reached **only** via domain services. No Temporal access. |
| **External data service** | Upstream schedules/catalog and related facts. Used to **enrich** create/fulfilment requests; surfaces airing that can drive auto create. No Temporal access. |
| **Orchestration + Temporal** | Owns durable fulfilment from DSL: workflows, waits, task queues. Interacts with Temporal together with domain services only—not BFF, DB, or external data. |
| **AI metadata service** | Given source-language long description, returns target-language variants for different surfaces. Called by metadata domain service; does not own workorder state or talk to Temporal. |

---

## 7. High-level fulfilment flow

Applies after a workorder exists (from UI or airing). Same for metadata, CC, AD—with different domain steps.

1. Config already exists; create request reaches **domain service** (via BFF or airing); domain enriches, persists (`NEW`), then starts fulfilment through **orchestration/Temporal**.
2. Workflow advances through DSL steps, for example:
   - Wait until proxy media is available (domain checks and updates status via DB).
   - Run domain work (e.g. metadata service calls AI, persists drafts via DB).
   - Hand off to vendor **manual review** and wait (hours to months, or until cancel).
   - Send completion notification; mark `COMPLETED`.
3. Terminal outcomes: **completed** or **cancelled** (saga-style compensation where needed).

Bulk Excel: BFF → domain service per row (or batch), same enrichment/persist/fulfil spine.

---

## 8. Architectural style and patterns

The system is an **async, event-aware, orchestration-saga platform** with durable workflows.

| Pattern | Where it shows up |
|---|---|
| **BFF** | Angular talks only to the BFF; BFF talks only to domain services (not Temporal/DB/external data). |
| **Service per capability** | Metadata, CC, AD, orchestration, external data, AI. |
| **Orchestration-based saga** | Multi-step fulfilment across services; cancel/compensate instead of one distributed transaction. |
| **Process manager / long-running process** | One Temporal workflow per workorder, possibly lasting a long time. |
| **State machine** | Workorder status progression, updated by domain services via DB service. |
| **Event-driven** | Airing event hits domain service to create workorders; proxy/review events advance fulfilment. |
| **Asynchronous messaging** | Domain fulfilment work via Temporal task queues. |
| **Durable execution** | Timers, retries, and long waits owned by Temporal. |
| **Human-in-the-loop** | Manual review is a durable wait on vendor outcome. |
| **Workers / bulkheads** | Each domain service owns its queue(s). |
| **DSL / interpreter** | Fulfilment steps defined per workorder type. |
| **Anti-corruption / enrichment** | External data service wraps upstream systems and enriches domain requests. |
| **Pipeline** | AI: translate long text, then compress into shorter variants. |
| **Transactional outbox** (recommended) | Reliably start fulfilment after the workorder is committed. |
| **Idempotency** | Safe retries; airing-triggered create must not duplicate an existing workorder. |

**Not the primary style:** pure choreography. Events appear at the edges (notably airing → domain create); **orchestration** owns fulfilment.

---

## 9. Design principles

1. **Config → workorder → fulfil** — fixed spine; config is mandatory before any order.
2. **Domain service is the convergence point** — UI (via BFF) and airing both create workorders through the domain service.
3. **BFF never touches DB, external data, or Temporal** — only domain services (and orchestration for Temporal) do.
4. **Only domain + orchestration talk to Temporal** — DB, external data, BFF, and AI do not.
5. **One workorder create, two triggers** — UI (advance) and airing (automatic) are equivalent after they reach the domain service.
6. **Airing creates orders, not assets** — ensures a workorder exists when the team did not pre-order.
7. **Order ≠ fulfilment** — create records intent; domain starts orchestration; domain + Temporal produce assets.
8. **Same fulfilment spine for all work types** — shared orchestration; different domain activities per asset type.

---

## 10. Technology map (summary)

| Layer | Stack |
|---|---|
| UI | Angular |
| BFF, DB, domain, orchestration, external data | Java |
| Workflow / durable execution | Temporal + flow DSL |
| Metadata AI | Python (FastAPI, LangChain / LangGraph) |
