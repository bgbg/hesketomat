# Interview Prep TAB

One screen corresponds to a single interview preparation workspace.

## Layout

Three-column split view, equal widths by default:

- **Left:** Notes
- **Middle:** Search
- **Right:** Outline Canvas

Columns are **resizable** via draggable dividers. Default ratio **1:1:1**.

---

## Top Bar (global)

- **Interview title** (editable inline)
- **Autosave status**: `Saving…` / `Saved`
- (Optional v1) Buttons: `Generate outline`, `Export`, `Help`

---

## Left Column — Notes (sticky notes)

### Purpose
Capture research and preparation content as vertically stacked “sticky notes”.

### Core constraints
- Notes are arranged **vertically only** (no horizontal canvas placement).
- Items inside a note are also **vertical**.

### Note types (hybrid)
1) **Bucket note**: a note that contains multiple items (text/images).
2) **Pinned item note**: a single item promoted to a standalone note card.

### Create note
- A **“+ New note”** button at the top of the Notes column.
- Creates an empty bucket note with an editable title.

### Note anatomy
Each note card includes:
- Title (editable)
- Drag handle (reorder notes)
- Items list
- (Optional) `Pin note` / `Delete note` actions

### Adding content to notes
Two provenance modes:

#### A) Web-clipped items (from Search results)
Must include a rich source row:
- favicon
- page title
- domain
- timestamp
- link icon
Clicking opens the source in a new tab.

#### B) Manual paste (user pasted text/image)
- No URL / source stored.
- UI distinction: **no source row** (no link icon/domain).

### Item actions (v1)
- Reorder item (drag handle)
- Delete item
- (Optional) Copy item text / open image in full size

---

## Middle Column — Search

### Purpose
Ask questions, search the web, review results, and clip content into notes.

### Components
1) **Search input** (question box)
2) **Search button** (or Enter to run)
3) Results area containing:
   - **LLM summary** at top (with citations)
   - **Web link results** list
   - **Image results** grid

### Web link result behavior (default)
- Clicking the result title opens in a **new tab**.
- Each result row has `Add to note`:
  - Choose existing note
  - Or `Add to new note…` (creates a new bucket note, then adds item)

### Image results behavior (default)
- Grid of thumbnails.
- Clicking a thumbnail opens the **source page in a new tab**.
- Hover actions include:
  - `Add to note` (choose existing or new note)

### LLM summary block (with citations)
- Shows a concise answer with citation markers.
- Clicking a citation opens the referenced source in a new tab.
- (Optional v1) `Add summary paragraph to note`.

---

## Right Column — Outline Canvas

### Purpose
A structured, editable interview outline with LLM-assisted editing.

### Document structure
- Supports headings/sections such as:
  - Intro
  - Guest bio
  - Themes
  - Questions
  - Closing
- Headings are **editable like normal text**.
- Headings can be **collapsed/expanded**.
- Includes a lightweight **Table of Contents** within the canvas area for navigation.

### Direct editing
- Typing, deleting, and rearranging text is supported.
- Autosave is always on.
- Undo/redo.

### LLM editing interaction (selection toolbar)
- Selecting text shows a floating mini-toolbar with actions:
  - Improve
  - Shorten
  - Expand
  - Change tone
  - Rewrite as questions
  - Custom prompt…
- Applying an action edits the selected text (replace selection) with undo support.

---

## Global behaviors

### Reordering
- Notes reorder vertically via drag.
- Items inside a note reorder vertically via drag.

### Source rules
- Anything added via Search is a **web clip** and stores a source card (rich citation).
- Manual paste items store **no source** and show no source row.

### Persistence
- Autosave across Notes and Canvas.
- One workspace per interview.

---

## Suggested v1 entities (optional for implementation)

- **Interview**
  - id, title, created_at, updated_at
- **Note**
  - id, interview_id, title, order_index, type: bucket|pinned
- **NoteItem**
  - id, note_id, type: text|image
  - content (text or image_url/blob ref)
  - provenance: web|manual
  - source (nullable): { url, title, domain, favicon_url, captured_at }
- **CanvasDoc**
  - interview_id, structured_content (rich text / blocks), updated_at
