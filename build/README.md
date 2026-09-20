# build/ — regenerate the exact submission files

These scripts produce the exact `.docx` and `.pptx` the challenge form expects.
They need Node.js. Run them from the repo root.

```bash
npm install docx pptxgenjs

# Brief Project Description  ->  FlowKeeper_Project_Description.docx
node build/build_docx.js

# Pitch deck  ->  FlowKeeper_Pitch.pptx
node build/build_deck.js

# Pitch deck PDF (needs LibreOffice)
soffice --headless --convert-to pdf FlowKeeper_Pitch.pptx
```

The polished HTML versions (`FlowKeeper_Pitch.html`, `FlowKeeper_Project_Description.html`)
render the same content and can be printed straight to PDF from a browser if you don't
have Node handy.
