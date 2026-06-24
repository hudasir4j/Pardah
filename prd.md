# Product Requirement Document (PRD)

## Product Vision
To build the world’s most accurate facial retrieval engine specifically optimized for the "Hijab-Transition" use case, wrapped in an empathetic, reassuring, and highly secure digital experience. Phase 0 focuses entirely on discovering and organizing digital footprints with 99% accuracy, offering women a safe space to find and manage their pre-transition images.

---

## Core Values & Design Philosophy
* **Empathetic Security:** Searching for past images can be an emotionally vulnerable process. The platform must feel like a supportive sanctuary, not a clinical surveillance tool.
* **Zero-Retention Privacy:** Absolute data transience. Users must have total peace of mind that their uploaded data and search findings vanish completely after use.
* **Editorial Clarity:** Information should be presented with high typographic elegance, soft colors, and thoughtful spacing to reduce user anxiety.

---

## Feature Breakdown (Prioritized for Retrieval)

| Feature | Description | Priority | Technical Requirement |
| :--- | :--- | :--- | :--- |
| **Multi-Reference Upload** | User uploads 3-5 photos (various angles/lighting, pre-hijab and current) to construct a robust biometric search profile. | **P0** | Frontend UI to support multi-file drag-and-drop; Backend API to aggregate files into a unified search query. |
| **Discovery Pipeline (Multi-Engine)** | Simultaneous, parallel search across web-scale facial recognition indices. | **P0** | Integration with FaceCheck.id API and/or PimEyes API. |
| **Verification Layer** | Cross-references engine results against original uploads to filter out false positives and calculate a match score. | **P0** | Secondary local facial-similarity check using Python's `DeepFace` library. Filter out results below 85% confidence. |
| **Context Extraction** | Automatically gathers metadata from the source URLs of discovered images. | **P1** | Headless browser scraper (Puppeteer/Playwright) to extract Page Title, Platform Type, and Publication Date. |
| **Graceful Scraping Fallback** | Prevents pipeline crashes if target sites block the metadata scraper. | **P1** | Error-handling logic that gracefully falls back to extracting and displaying the raw base domain (e.g., "instagram.com") if scraping fails. |
| **Digital Footprint Grouping** | Automatically categorizes discovered links by platform type for structured review. | **P1** | Categorization logic using RegEx or lightweight LLM tagging (e.g., Social, Archives, Blogs, News). |
| **Instant Purge (Wipe Session)** | One-click or timeout-driven absolute destruction of user data. | **P0** | Session-ending function that hard-deletes all uploaded assets and results from memory, databases, and temporary S3 buckets. |

---

## Visual & UX Identity (Retro-Therapeutic / Soft Editorial)

### 1. Aesthetic Direction
* **Style:** Warm, nostalgic, editorial, and deeply reassuring. Clean layouts with rounded corners, pill-shaped UI badges, and soft, organic divider lines. Avoid all clinical, forensic, or brutalist styling.
* **Color Palette:**
    * *Primary Background:* Warm Cream / Off-White (`#F9F6F0`)
    * *Text:* Deep Charcoal (`#2A2A2A`) for soft readability (avoid pure black)
    * *Accents:* Soft Sage Greens, Powder Blues, Pastel Yellows, and a warm Terracotta/Burnt Amber for primary call-to-action buttons.
* **Typography:**
    * *Headings:* High-contrast, elegant Serif (e.g., *Playfair Display* or *Instrument Serif*)
    * *Body/Technical Data:* Clean, highly legible Sans-Serif (e.g., *Inter* or *DM Sans*).

### 2. Dashboard & Card Layout
The findings dashboard will display results in a structured, clean masonry grid featuring **Discovery Cards**:
* **Thumbnail:** Found image presented with softly rounded edges.
* **Match Indicator:** A gentle pill badge (e.g., a soft green badge stating "High Match" instead of a raw mathematical percentage if it helps readability).
* **Context Snippet:** Clearly displayed Page Title and detected platform type.
* **Action Button:** An outlined or softly filled pill button reading "Review Link" or "View Source".

---

## Data Safety & Privacy Constraints

### 1. Ephemeral Infrastructure
* **Biometric In-Memory Processing:** Facial templates and vectors generated for the search pipeline must be processed entirely in-memory and encrypted.
* **No Persistent Logging:** No found URLs, image metadata, or user biometric profiles may be written to persistent database storage. 
* **Session Lifecycle:** Supabase database records are strictly limited to temporary session metadata. All temporary storage locations (AWS S3 / Supabase Storage) must be bound by a strict **30-minute hard deletion lifecycle policy** or immediate user-triggered purge.

---

## Technical Stack

* **Frontend:** Next.js (App Router) + Tailwind CSS (configured with the custom warm cream and soft retro palette).
* **Backend:** FastAPI (Python) — required for native orchestration of the `DeepFace` library and fast parallel API routing.
* **Database:** Supabase (PostgreSQL) — exclusively utilized for ephemeral session states and metadata management.
* **Storage:** AWS S3 or Supabase Storage (strictly configured for temporary, short-lived asset hosting).