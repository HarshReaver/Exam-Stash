# Night Before: design direction

Site: pyq.harver.in. Previous-year papers, question banks and notes for TCET IT students, shared by Harsh (IT Batch 2027).

## Design Read
Reading this as: a study-file library for engineering students who mostly open it on a phone the night before an exam, in a native file-app style, dial ENERGY 1 / RHYTHM 1 / MOTION 1.

## Owner direction (Harsh, 23 Nov 2026)
- Round 1 (ruled paper, harver.in caption box, photocopy stack) was rejected as AI-looking, portfolio-copying or shadow-heavy.
- Round 2: he picked the sidebar layout (E) with the file rows of option D (coloured PDF / XLSX / DOCX labels, Open and Download on every row).
- Dark by default, with a working light switch. A font real apps use. Colourful. Plain, helpful copy, no persona.

## Dials
- ENERGY 1: it is a tool. People arrive with a subject in mind and leave with a file.
- RHYTHM 1: every subject page has the same order (papers, question banks, notes). Uniformity is deliberate: scanning many subjects fast beats variety.
- MOTION 1: hover and focus states only. Nothing animates; pages load into the same frame.

## Decisions, one line each
- Typeface: the system UI stack (Segoe UI, San Francisco, Roboto). It is what native apps use, costs no download and reads well at small sizes.
- Layout: sidebar of semesters and subjects on desktop, a native "Jump to subject" select on phones. Harsh found it the easiest to navigate.
- Colour, semesters: each semester owns one colour (III teal, IV violet, V amber, VI pink, VII sky). It answers "where am I" at a glance and is the "colourful" he asked for. This is the identity motif: a semester colour stripe on the sidebar group, the subject header and the home list.
- Colour, file types: PDF red, XLSX green, DOCX blue, the colours people already link to those formats. Text labels, not icons.
- Neutrals: near-black background (#0f1012) and a slightly lighter sidebar; light mode is warm off-white. Neutrals carry the layout so the two colour systems stay readable.
- Accent: the current semester's colour is the one accent on a page (stripe, links, focus ring). The rest is neutral.
- Surfaces: flat. 1 px lines separate rows. No shadows anywhere (Harsh reads hard shadows as vibe-coded).
- Radius: 6 px on lists and inputs, 4 px on small controls. No pills.
- Buttons: Open and Download are text actions in the semester colour with 44 px tap areas, so a page with ten files does not shout ten times.
- Icons and illustration: none. The file-type label and the page content do the work.
- Viewer: scanned papers are shown as page images, because phone browsers (Chrome on Android) do not open PDFs inline. The original PDF is one tap away.
- Question banks from Excel and Word become readable pages, keeping the original colour coding with an on-page legend. The original file stays downloadable.
- States: search has an empty state; page images show a loading frame and an error message that points to the PDF; missing papers or banks are simply not listed.
- Copy: plain and specific. No em dashes, no hype words, no invented numbers. Every count on the site is computed from the files.

## Hard rules carried from the owner's list
No purple gradient, no gradient text, no glow, no blobs, no emoji in navigation, no label above the headline, no hype words, no stat banners, no tiny all-caps labels, no icon boxes, no bouncing, no fake reviews.
