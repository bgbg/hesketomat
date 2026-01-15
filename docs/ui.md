# Interview Prep Tab — UI Specification

## Overview
This document outlines the UI structure for the new "Interview Prep" tab, designed to help podcasters prepare for interviews.

## Core Layout
The tab features a **three-column layout** designed for a research-to-outline workflow:

1.  **Left Column: Notes & Context** (30%)
    -   **Context Area**: A persistent text area at the top for entering "Interview Background" (interviewee bio, goal, audience). This context drives future AI suggestions.
    -   **Notes List**: A vertical list of "Sticky Notes" or "Buckets".
        -   Each note has a title and a list of items.
        -   Notes can be reordered via drag-and-drop.
        -   Items within notes can be text snippets or images.
        -   Items often come from search results (provenance tracking).
        -   Notes can be selected (highlighted) to be the target for new items.

2.  **Middle Column: Search & Discovery** (35%)
    -   **Search Bar**: Input for queries.
    -   **AI Summary**: A generated summary of the search topic with citations.
    -   **Web Results**: List of web pages with titles, domains, and snippets.
        -   **Action**: "Add to Note" button adds the snippet to the currently selected note.
    -   **Image Results**: Grid of relevant images.
        -   **Action**: "+" button adds the image to the currently selected note.

3.  **Right Column: Outline Canvas** (35%)
    -   **Structured Editor**: A block-based editor for the interview outline.
    -   **Block Types**: Headings and Paragraphs.
    -   **Interaction**: Blocks can be edited directly. New blocks can be added.
    -   **AI Assistance**: (Mocked) Floating toolbar for text refinement (Shorten, Improve, etc.).

## Navigation & Persistence
-   **Projects Tab**: A separate main tab listing all saved interview projects.
    -   Shows project title, last modified date, and stats.
    -   Allows creating new projects or loading existing ones.
-   **Menu**: A dropdown in the Interview Prep tab header.
    -   **New Interview**: Clears the workspace.
    -   **Save Changes**: Persists the current state to LocalStorage.
    -   **Reload**: Refreshes the view from saved state.

## Visual Style
-   **Framework**: Chakra UI.
-   **Theme**: Clean, light/dark mode compatible.
-   **Interactivity**: Heavy use of drag-and-drop (Framer Motion) and hover states for a dynamic feel.
