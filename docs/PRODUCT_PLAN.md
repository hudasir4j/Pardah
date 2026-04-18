# Pardah Product Plan: From MVP to Full Platform

**Goal:** A platform where a hijabi uploads her photo → we find images of her across the web → she gets a clear, legitimate path to get them taken down. Keep the “wow” factor. No shady automation.

---

## 1. Core Principle: Discovery in the App, Takedown by the Book

- **Hero experience stays in the web app:** Upload photo + name → we search multiple sources → face-matched results in one place. This is the differentiator.
- **Takedown = guided, not automated:** We don’t auto-submit reports or scrape Instagram. We show each match, say where it lives (Google vs. Instagram vs. random site), and give one-click/copy-paste steps to use **official** reporting tools. Transparent and ToS-friendly.
- **Chrome extension = optional helper:** Only for “I’m already on a page with my image; make reporting easier.” Discovery still happens in Pardah.

---

## 2. Phase 1: Better Search (Including “Google Images”)

**Problem:** MVP only uses Bing; users expect Google Images.

**Reality:** Google doesn’t offer a public “search images by keyword” API for this. Two legitimate options:

| Option | What it does | Pros | Cons |
|--------|----------------|------|------|
| **SerpApi / Serper / ValueSerp** | They run Google (and others) and return structured results, including **Google Images** (image URL, page URL, thumbnail). | Real Google Image results, legal, no scraping. | Paid (free tiers available). |
| **Google Custom Search JSON API** | Official API; can do image search. | Official, predictable. | 100 queries/day free; results are more “web” than raw image. |

**Recommendation:**

1. **Add a “Google Images” source via SerpApi or Serper** (e.g. “Google Images” in the UI). Same search terms you already use (name, name + “instagram”, etc.). Store `image_url`, `page_url`, `source: "google-images"` so you can show “Found on Google Images” and still open the right URL for removal.
2. **Keep Bing** (current flow) as a second source. Combined result set, then dedupe by image URL or perceptual hash if you want.
3. **Single pipeline:** Same face embedding + same `match_faces()` step; only the “where we get candidate images from” changes. So: **SerpApi (Google Images) + Bing → download / fetch thumbnails → face match → same review UI.**

**Implementation outline:**

- New module, e.g. `search_google_images.py`, that:
  - Takes `query`, `max_results`.
  - Calls SerpApi/Serper “Google Images” endpoint.
  - Returns list of `{ "url": image_url, "page_url": ..., "source": "google-images" }`.
- In `main.py` (or a small orchestrator), run both:
  - `search_images_bing(...)` (current)
  - `search_google_images(...)` (new)
- Merge, dedupe by URL, then pass into existing `match_faces()`. No change to DeepFace or review flow.

**User-facing:** “We search Google Images and Bing for you.” That directly addresses “we want Google.”

---

## 3. Phase 2: Straightforward, Legitimate Takedown Flow

**Problem:** Current MVP has “Report to Google” and backend has email/DMCA templates, but it’s not obvious *where* each image lives or what to do for non-Google hosts (Instagram, Facebook, etc.). So it doesn’t feel “streamlined.”

**Idea:** For each match, we know the **host** (e.g. google.com, instagram.com, facebook.com, or “other”). We give a **host-specific action** so the user has one clear path per result.

**Data you already have (or can add):**

- `url`: the image URL or page URL from the search result.
- From `url` you can derive `host` (e.g. `instagram.com`, `google.com`).

**Takedown matrix:**

| Host type | What we show | Action (no automation) |
|-----------|----------------|--------------------------|
| **Google (indexed)** | “This appears in Google’s index.” | One-click: open Google Removal Tool / outdated content form with URL prefilled (you already do this). |
| **Instagram** | “Host: instagram.com” + link to the post. | “Report on Instagram” → button opens Instagram’s **official** report/help flow; short in-app copy: “Choose ‘I’m in this photo and I don’t like it’ (or equivalent).” We don’t auto-fill or submit. |
| **Facebook** | Same idea. | Link to Facebook’s reporting/removal page + one sentence of guidance. |
| **Other site** | “Host: example.com.” | “Email site owner” → show your existing **email template** (GDPR/removal) with URL and optional hash; “Copy” button. Optionally “DMCA template” for users who own the photo. |

**UI flow:**

1. In the review step, under each match: show **“Where it appears”** (e.g. “Google Images”, “Instagram”, “example.com”).
2. One primary button per host:
   - **Google** → “Request removal from Google” (opens your existing removal URL).
   - **Instagram / Facebook** → “Open [Platform] report page” (opens official URL) + 1 line of instructions.
   - **Other** → “Copy email to site owner” (and optionally “Copy DMCA template”).
3. Optional: “Copy link” so they can paste it into any form.

**Backend:**

- Add a small helper: `get_takedown_action(image_url)` → `{ "host": "instagram", "action": "report", "report_url": "https://help.instagram.com/...", "instructions": "..." }`. You can hardcode known hosts (google, instagram, facebook) and fallback to “other” with email template.
- Reuse `report_generator.py`: `generate_removal_email_body`, `generate_google_images_removal_link_v2`, etc. No need to change those; just call them from the new “takedown action” logic.

**Result:** One screen per match: “We found it here → do this one thing.” No automation, no grey-area scraping; just clear, legitimate steps. That’s the “streamlined” takedown.

---

## 4. Phase 3: Chrome Extension (Optional “Wow” Add-On)

**Problem:** A full extension that “goes through Instagram and automates reporting” feels shady and is likely against ToS. It also shifts the hero moment from “upload and we find everything” to “we help you report on one site.”

**Better role for an extension:** **Quick Report from current page.**

- User is **already** on a page (Instagram, Facebook, random blog) that has her image.
- She clicks the extension → “Report this page with Pardah.”
- Extension sends the **current tab URL** (and optionally a selected image URL) to the Pardah app or a simple backend endpoint.
- Pardah then:
  - Shows the same **guided takedown** (e.g. “This is Instagram → open Instagram report”), or
  - Opens the removal form with that URL prefilled.
- So: **discovery** still happens in the main app (upload → search → matches). The extension is a shortcut when she’s already on a problematic page.

**What we don’t do:** No logging into Instagram/Facebook, no auto-clicking “Report,” no scraping feeds. Just “current URL → Pardah → same official reporting flow.”

That keeps the extension useful without the “shady” or ToS-risky part.

---

## 5. Technical Summary

| Area | Current | Change |
|------|---------|--------|
| **Search** | Bing only (bing-image-downloader) | Add SerpApi/Serper for Google Images; keep Bing; merge + dedupe. |
| **Face pipeline** | DeepFace, match_faces, threshold | No change. |
| **Takedown** | Generic “Report to Google” + backend templates | Host-aware actions: Google → removal link; Instagram/Facebook → official report link + short instructions; Other → email/DMCA template + copy. |
| **Extension** | N/A | Optional: “Send current page URL to Pardah” → same guided takedown. |

---

## 6. What We’re Explicitly Not Doing

- **No automated reporting:** We don’t submit forms on Instagram/Facebook/Google on the user’s behalf. We open the **official** form and guide.
- **No scraping of social feeds:** No “scan all of Instagram.” Discovery = search engines (Google Images, Bing) + user’s search terms. Extension only uses the URL of the page the user is already on.
- **No fake or misleading flows:** All links are to real, official reporting/removal pages. No “looks like reporting but doesn’t.”

---

## 7. Suggested Order of Work

1. **Phase 1 (Search):** Integrate SerpApi or Serper for Google Images; merge with Bing; keep same review UI. Ship “We search Google Images and Bing.”
2. **Phase 2 (Takedown):** Add host detection and host-specific actions in the app; one clear button/link per match. Ship “Streamlined removal” with official links only.
3. **Phase 3 (Extension):** Small extension: “Send this page to Pardah” → open app or prefill removal flow. Optional.

This keeps the “upload a photo → we find your images → you take them down” story in the main product, adds the Google Images coverage users want, and makes takedown straightforward and legitimate without relying on a Chrome extension for the core value.
