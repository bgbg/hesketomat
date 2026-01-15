# Interview Prep Tab — v1 (wireframes, flows, state model)

This document complements `ui.md` with:
- Wireframe-level component list
- Key user flows (Search → clip → outline edit)
- Minimal UI state model for implementation

---

## 1) Wireframe-level component list

### 1.1 Global shell

**A. AppFrame**
- **TopBar**
  - **MenuButton** (New Interview, Save, Reload)
  - TitleInlineEdit
  - SaveStatusIndicator
  - PrimaryActions
    - GenerateOutlineButton
    - ExportButton (optional v1)
    - HelpButton (optional v1)
  - **ProjectsTab** (Separate view for managing multiple projects)
- **ColumnsLayout**
  - LeftColumn (Notes + Context)
  - ColumnDivider (resizable)
  - MiddleColumn (Search)
  - ColumnDivider (resizable)
  - RightColumn (Outline Canvas)

**B. ColumnDivider**
- Drag handle
- Double-click reset to 1:1:1 (optional)
- Cursor + hover affordance

---

### 1.2 Left column — Notes & Context

**A. ContextArea (Fixed Top)**
- Background Context Textarea (always visible)
- "Interview Background" Label

**B. NotesPanel**
- HeaderRow
  - `+ New note` button
- NotesList (vertical, sortable via Drag & Drop)
  - NoteCard

**C. NoteCard**
- NoteHeader
  - NoteTitleInlineEdit
  - DragHandle (reorder note)
  - NoteMenu (⋯)
    - DeleteNote
- NoteItemsList (vertical)
  - NoteItemCard
- DropZone (placeholder for dragging items in)

**D. NoteItemCard**
- ItemBody
  - TextBlock OR ImageBlock
- ItemSourceRow (shown only if provenance=web)
  - LinkIcon
  - Favicon
  - Local domain text
- ItemActions
  - DragHandle (reorder within note)
  - DeleteItem

---

### 1.3 Middle column — Search

**A. SearchPanel**
- SearchInputRow
  - QueryInput
  - SearchButton
- SearchResultsArea
  - LLMSummaryCard (with citations)
  - WebResultsList
  - ImageResultsGrid

**B. LLMSummaryCard**
- SummaryText (with citation markers)
- CitationList
  - Each citation opens source in new tab

**C. WebResultRow**
- TitleLink (opens in new tab)
- Snippet
- ResultMeta (domain, favicon)
- AddToNoteButton ("Add to Note")
  - Adds to the **currently selected note**

**D. ImageResultsGrid**
- ImageThumbCard
  - Thumbnail
  - HoverActions
    - AddToNoteButton (+)
      - Adds to the **currently selected note**

---

### 1.4 Right column — Outline Canvas

**A. CanvasPanel**
- CanvasHeader
  - (Optional) GenerateOutlineButton
- CanvasEditor (structured document)
  - HeadingBlock
  - ParagraphBlock
- Add New Block Placeholder

**B. SelectionToolbar (floating)**
Appears on text selection:
- Improve
- Shorten
- ChangeTone

---

## 2) User flows

### 2.1 Search → add to selected note
1. User clicks a Note to select it (highlighted blue).
2. User searches for a term.
3. User clicks "Add to Note" on a result.
4. Item is added to the selected note.
5. Toast notification confirms addition.

### 2.2 Reordering
1. User grabs the drag handle (☰) of a Note.
2. User drags it up/down to reorder.
3. User releases to save new order.

### 2.3 Persistence & Projects
1. User clicks "Menu" -> "Save Changes".
2. State (Notes, Context, Outline) is saved to LocalStorage.
3. User navigates to "Projects" tab.
4. User sees list of saved projects (mocked for now).
5. User clicks a project to load its state into the Preparation tab.

---

## 3) Minimal UI state model (objects/fields)

### 3.1 Domain entities

#### Project (Metadata)
- `id: string`
- `title: string`
- `lastModified: string (ISO)`
- `noteCount: number`
- `hasContext: boolean`

#### Interview (Workspace State)
- `interviewTitle: string`
- `backgroundContext: string`
- `notes: Note[]`
- `outline: CanvasBlock[]`
- `timestamp: string (ISO)`

#### Note
- `id: string`
- `title: string`
- `items: NoteItem[]`

#### NoteItem
- `id: string`
- `type: "text" | "image"`
- `content: string` (text or image URL)
- `provenance: "web" | "manual"`
- `source?: { title, domain }`

#### CanvasBlock
- `id: string`
- `type: "heading" | "paragraph"`
- `text: string`

