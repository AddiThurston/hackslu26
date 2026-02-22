# hackslu26

## Canvas Physical Document Scanner

Collaborators: Addison Thurston, Henry Morgan, Henry Beblo, Carter DeLargy

### What It Does:

Creates assignments/quizzes on Canvas based off of images/text prompts.

### How Does It Work?

If an image is being entered, it's first taken and transformed via our Geometric Filter so that it's prepared to be read for AI. 

Then, the fitted photo is passed through to the Google Cloud Vision API.

This extracted text is then processed and formatted (with parameters separated with '|') with the Gemini Pro 2.5 API.

This formatted text is then parsed and passed through to the Canvas API, where it can be published on Canvas.

## What Is Needed?

API keys for 'Google Cloud Vision' and 'Gemini Pro 2.5' are needed.
