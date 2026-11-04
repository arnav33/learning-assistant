# AI Layer — Low-Level Design (Metadata Translation)

## 1. APIs

| Method & path | Purpose |
|---|---|
| `POST /v1/metadata-localizations` | Localize a full metadata set; return localized fields in the response (no AI-side persistence) |

Persistence of results is owned by the Java **domain service** → **data service**, not the AI layer.

**Request (conceptual)**

```json
{
  "source_language": "en-US",
  "target_language": "ja-JP",
  "required_descriptions": ["desc400", "desc300", "desc150", "desc80"],
  "metadata": {
    "title": "…",
    "description": "…",
    "audio_format": "Dolby Atmos | Surround | Dolby Digital | DTS:X | …",
    "cast": [ … ],
    "director": [ … ],
    "producer": [ … ]
  }
}
```

`required_descriptions` drives conditional routing after the long-description step (omit lengths the caller does not need).

**Response (conceptual)** — only includes requested description lengths plus other localized fields.

---

## 2. LangChains

A chain can contain multiple nodes (prompt → LLM → parse → validate, etc.). Graph state holds intermediate results; the API returns the final localized payload.

| Chain | Nodes (conceptual) | Purpose |
|---|---|---|
| `title_chain` | translate (+ optional validate) | Localize title |
| `cast_chain` | translate (+ optional validate) | Localize cast |
| `director_chain` | translate (+ optional validate) | Localize director |
| `producer_chain` | translate (+ optional validate) | Localize producer |
| `audio_format_chain` | localize label (+ optional validate) | Localize audio format |
| `long_description_chain` | `translation_400` (+ optional validate) | Translate source description → ≈400 (base for shorter lengths) |
| `desc300_chain` | `compress_300` (+ optional validate) | Compress from long → ≈300 |
| `desc150_chain` | `compress_150` (+ optional validate) | Compress → ≈150 |
| `desc80_chain` | `compress_80` (+ optional validate) | Compress → ≈80 |
| `validate_chain` | length / schema checks | Final validation before API response |

---

## 3. LangGraphs

### `metadata_localize_graph`

Independent field chains can run in parallel. Description path is sequential from long, then **conditionally** fans out to shorter lengths.

```
START
  → title_chain, cast_chain, director_chain, producer_chain, audio_format_chain  (parallel)
  → long_description_chain
       │
       └─ add_conditional_edges(
            "long_description_chain",
            check_required_descriptions,
            {
              "desc300": "desc300_chain",
              "desc150": "desc150_chain",
              "desc80":  "desc80_chain",
            }
          )
  → validate_chain
  → END
```

`check_required_descriptions(state)` reads `required_descriptions` (and/or what is already present) and returns the list of next node names to run—same idea as multi-dest conditional edges in LangGraph.

| Node / chain after long | When |
|---|---|
| `desc300_chain` | `"desc300"` required |
| `desc150_chain` | `"desc150"` required |
| `desc80_chain` | `"desc80"` required |

Shorter lengths compress from the recorded long (400) output; they are not separate translations from the source language.
