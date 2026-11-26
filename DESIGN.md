# Exam Stash: design direction

Site: stash.harver.in. Previous-year papers, question banks and notes for TCET IT students, shared by Harsh (IT Batch 2027). Called "Night Before" at pyq.harver.in for its first day; renamed by Harsh on 23 Nov 2026.

## Design Read
Reading this as: a study-file library for engineering students who mostly open it on a phone, often late before an exam, in a native file-app style, dial ENERGY 1 / RHYTHM 1 / MOTION 1.

## Owner direction (Harsh, 23 Nov 2026)
- Round 1 (ruled paper, harver.in caption box, photocopy stack) was rejected as AI-looking, portfolio-copying or shadow-heavy.
- Round 2: he picked the sidebar layout (E) with the file rows of option D (coloured PDF / XLSX / DOCX labels, Open and Download on every row).
- Dark by default, with a working light switch. A font real apps use. Colourful. Plain, helpful copy, no persona.
- Every semester opens and closes, so nobody scrolls past semesters they don't need.
- Papers from other branches sit in one "Other branches" section, because the semesters follow the IT syllabus.

## Dials
- ENERGY 1: it is a tool. People arrive with a subject in mind and leave with a file.
- RHYTHM 1: every subject page has the same order (papers, question banks, notes). Uniformity is deliberate: scanning many subjects fast beats variety.
- MOTION 1: hover and focus states only. Sections open instantly; nothing animates.

## Decisions, one line each
- Typeface: the system UI stack (Segoe UI, San Francisco, Roboto). It is what native apps use, costs no download and reads well at small sizes.
- Layout: sidebar of sections and subjects on desktop, a native "Jump to subject" select on phones. Harsh found it the easiest to navigate.
- Open and close: native details/summary in the sidebar and on the home page. The sidebar opens only the current subject's semester; the home page starts closed, opens a semester from a /#sem-N link, and search opens the semesters with matches. A drawn chevron shows the state, no icon font.
- Colour, sections: each section owns one colour (I periwinkle, II orange, III teal, IV violet, V amber, VI pink, VII sky, Other branches grey). It answers "where am I" at a glance and is the "colourful" he asked for. This is the identity motif: a colour stripe on the section, the subject header and the home list. Other branches is grey on purpose: it is outside the IT colour code.
- Colour, file types: PDF red, XLSX green, DOCX blue, the colours people already link to those formats. Text labels, not icons.
- Neutrals: near-black background (#0f1012) and a slightly lighter sidebar; light mode is warm off-white. Neutrals carry the layout so the two colour systems stay readable.
- Accent: the current section's colour is the one accent on a page (stripe, links, focus ring). The rest is neutral.
- Surfaces: flat. 1 px lines separate rows. No shadows anywhere (Harsh reads hard shadows as vibe-coded).
- Radius: 6 px on lists, inputs and section headers, 4 px on small controls. No pills.
- Buttons: Open and Download are text actions in the section colour with 44 px tap areas, so a page with ten files does not shout ten times.
- Feedback, not "contact" (Harsh: people send more when it is feedback): the Marvel Timelines pattern, a "Help improve Exam Stash" strip in every footer opening a native dialog with optional stars, a topic, topic-specific fields for sending a paper (subject, semester, type, file link) and optional name and email. Subject "Exam Stash: new message, <topic>" feeds a Gmail label. The stars are the only icon: a rating needs them.
- Professional but simple: a Privacy and use page and a footer with the not-affiliated line, who owns the files, and the copyright line.
- His annotations: side notes from his sheets appear under their question; each converted sheet shows a colour key (its own legend, or his usual blue/red/green pattern).
- Icons and illustration: none. The file-type label and the page content do the work.
- Viewer: scanned papers are shown as page images, because phone browsers (Chrome on Android) do not open PDFs inline. The original PDF is one tap away.
- Question banks from Excel and Word become readable pages, keeping the original colour coding with an on-page legend. The original file stays downloadable.
- States: search has an empty state; page images show a loading frame and an error message that points to the PDF; the form shows sending, sent and failed states; missing papers or banks are simply not listed.
- Copy: plain and specific. No em dashes, no hype words, no invented numbers. Every count on the site is computed from the files.

## Hard rules carried from the owner's list
No purple gradient, no gradient text, no glow, no blobs, no emoji in navigation, no label above the headline, no hype words, no stat banners, no tiny all-caps labels, no icon boxes, no bouncing, no fake reviews.
